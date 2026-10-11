import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { createHash } from 'node:crypto';

const source = process.cwd();
const cli = join(source, 'node_modules', '@gef-bootstrap', 'cli', 'bin', 'gef.mjs');
assert.ok(existsSync(cli), 'Local GEF CLI is missing; install the pinned package with npm ci.');

const tempBase = resolve(process.env.NEX_GEF_TEST_TMP || tmpdir());
mkdirSync(tempBase, { recursive: true });
const fixtureRoot = mkdtempSync(join(tempBase, 'nex-gef-collision-'));
const fixture = join(fixtureRoot, 'repository');
let passed = false;

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd || source,
    encoding: 'utf8',
    timeout: 60_000,
    env: { ...process.env, GIT_OPTIONAL_LOCKS: '0' },
  });
  assert.ifError(result.error);
  assert.notEqual(result.status, null, `Command timed out: ${command} ${args.join(' ')}`);
  return { exitCode: result.status, stdout: result.stdout.trim(), stderr: result.stderr.trim() };
}

function gitStatus(path) {
  const result = run('git', ['-c', 'core.fsmonitor=false', '--no-optional-locks', 'status', '--porcelain', '-z', '--untracked-files=all'], { cwd: path });
  assert.equal(result.exitCode, 0, `git status failed in collision fixture: ${result.stderr}`);
  return result.stdout;
}

try {
  const clone = run('git', ['clone', '--quiet', '--local', '--no-hardlinks', '--no-checkout', source, fixture]);
  assert.equal(clone.exitCode, 0, `Could not create isolated collision fixture: ${clone.stderr}`);
  const checkout = run('git', ['checkout', '--quiet', '--detach', 'HEAD'], { cwd: fixture });
  assert.equal(checkout.exitCode, 0, `Could not checkout exact fixture HEAD: ${checkout.stderr}`);

  const stateDirectory = join(fixture, '.gef');
  const stateFile = join(stateDirectory, 'init-state.json');
  mkdirSync(stateDirectory, { recursive: true });
  const sentinel = 'user-owned collision sentinel\n';
  writeFileSync(stateFile, sentinel);
  const add = run('git', ['add', '--', '.gef/init-state.json'], { cwd: fixture });
  assert.equal(add.exitCode, 0, `Could not stage collision sentinel: ${add.stderr}`);
  const commit = run('git', [
    '-c', 'user.name=NEX isolated test',
    '-c', 'user.email=nex-test@example.invalid',
    'commit', '--quiet', '-m', 'fixture: establish user-owned GEF collision',
  ], { cwd: fixture });
  assert.equal(commit.exitCode, 0, `Could not commit isolated collision sentinel: ${commit.stderr}`);
  assert.equal(gitStatus(fixture), '', 'Collision fixture must be clean before the apply attempt.');

  const preview = run(process.execPath, [cli, 'init', '--target', fixture, '--json']);
  assert.equal(preview.exitCode, 0, `Collision preview failed: ${preview.stderr}`);
  const previewResponse = JSON.parse(preview.stdout);
  assert.equal(previewResponse.ok, true, 'Collision preview did not produce a plan.');
  assert.equal(previewResponse.value.effect, 'NONE', 'Collision preview must remain read-only.');
  assert.equal(previewResponse.value.plan.install.state, 'READY', 'Collision fixture install plan is not ready.');
  assert.equal(gitStatus(fixture), '', 'Collision preview changed the fixture working tree.');

  const before = createHash('sha256').update(readFileSync(stateFile)).digest('hex');
  const apply = run(process.execPath, [cli, 'init', '--target', fixture, '--apply', '--json']);
  assert.notEqual(apply.exitCode, 0, 'GEF init apply unexpectedly overwrote an existing state file.');
  const response = JSON.parse(apply.stdout);
  assert.equal(response.ok, false, 'Collision apply was not rejected.');
  assert.equal(response.terminal, 'BLOCKED', 'Collision apply did not end in BLOCKED.');
  assert.equal(response.error.effectStatus, 'NONE', 'Collision rejection reported a filesystem effect.');
  assert.equal(
    response.error.reasonCode,
    'gef.precondition.mutation_refused',
    'GEF must report a governed mutation refusal, not an unrelated blocked state.',
  );
  // The published CLI JSON projection does not expose nested transactionReason metadata.
  // Verify the public refusal reason AND its specific non-overwrite summary instead.
  assert.match(
    response.error.summary ?? '',
    /(?:existing|already present|not absent|collision|overwrite)/i,
    `GEF mutation refusal was not demonstrably due to an existing state-file collision: ${response.error.summary ?? 'NO_SUMMARY'}`,
  );
  assert.equal(
    createHash('sha256').update(readFileSync(stateFile)).digest('hex'),
    before,
    'GEF changed the user-owned collision sentinel.',
  );
  assert.equal(gitStatus(fixture), '', 'Collision rejection changed the fixture working tree.');
  assert.equal(existsSync(join(fixture, '.gef-private')), false, 'Blocked collision left private transaction artifacts.');

  console.log(JSON.stringify({
    result: 'PASS',
    fixtureHead: execFileSync('git', ['rev-parse', 'HEAD'], { cwd: fixture, encoding: 'utf8' }).trim(),
    applyExitCode: apply.exitCode,
    terminal: response.terminal,
    reasonCode: response.error.reasonCode,
    effectStatus: response.error.effectStatus,
    userOwnedStatePreserved: true,
    fixtureCleanAfterRefusal: true,
    privateArtifactsAfterRefusal: false,
  }));
  passed = true;
} finally {
  if (passed && !existsSync(join(fixture, '.gef-private'))) {
    rmSync(fixtureRoot, { recursive: true, force: true });
  } else {
    console.error(`Preserved isolated collision fixture for inspection: ${fixtureRoot}`);
  }
}
