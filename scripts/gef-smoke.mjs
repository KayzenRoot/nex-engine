import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync, lstatSync, readdirSync, readFileSync, readlinkSync } from 'node:fs';
import { join } from 'node:path';
import { createHash } from 'node:crypto';

// CI-only GEF smoke: never resolve Git through inherited, potentially writable PATH entries.
// These OS-managed locations are not writable by the non-admin test identity.
// The Node interpreter and GEF CLI are invoked by absolute paths.
const fixedExecutablePath = process.platform === 'win32'
  ? 'C:\\Program Files\\Git\\bin;C:\\Windows\\System32;C:\\Windows'
  : '/usr/bin:/bin';
const childEnvironment = Object.fromEntries(
  Object.entries(process.env).filter(([key]) => key.toUpperCase() !== 'PATH'),
);
childEnvironment.PATH = fixedExecutablePath;
childEnvironment.GIT_OPTIONAL_LOCKS = '0';

const target = process.cwd();
const cli = join(target, 'node_modules', '@gef-bootstrap', 'cli', 'bin', 'gef.mjs');

assert.ok(existsSync(cli), 'Local GEF CLI is missing; install the pinned package with npm ci.');

function run(args) {
  const result = spawnSync(process.execPath, [cli, ...args], {
    cwd: target,
    encoding: 'utf8',
    timeout: 30_000,
    env: childEnvironment,
  });
  assert.ifError(result.error);
  assert.notEqual(result.status, null, `GEF command timed out: ${args.join(' ')}`);
  return { exitCode: result.status, stdout: result.stdout.trim(), stderr: result.stderr.trim() };
}

function gitStatus() {
  const result = spawnSync('git', [
    '-c', 'core.fsmonitor=false',
    '--no-optional-locks',
    'status', '--porcelain', '-z', '--untracked-files=normal',
  ], {
    cwd: target,
    encoding: 'utf8',
    timeout: 10_000,
    env: childEnvironment,
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, `git status failed: ${result.stderr}`);
  return result.stdout;
}

function parseJson(command, result) {
  assert.ok(result.stdout, `${command} emitted no JSON output`);
  try {
    return JSON.parse(result.stdout);
  } catch (error) {
    assert.fail(`${command} emitted invalid JSON: ${error.message}`);
  }
}

function requireObservedRepository(label, repository, expectedState) {
  const observation = repository && typeof repository === 'object' ? repository : null;
  const verdict = observation?.verdict ?? null;
  if (verdict === null || observation.dirtiness === 'UNKNOWN') {
    const details = {
      category: 'GEF_REPOSITORY_OBSERVATION_INCOMPLETE',
      platform: process.platform,
      nodeVersion: process.version,
      command: label,
      expectedState,
      dirtiness: observation?.dirtiness ?? 'UNKNOWN',
      observationLimits: observation?.observationLimits ?? ['REPOSITORY_OBSERVATION_ABSENT'],
      gitToolchain: typeof doctorJson === 'object'
        ? {
            presence: doctorJson.value.doctor.toolchain?.git?.presence ?? 'UNKNOWN',
            probeStatus: doctorJson.value.doctor.toolchain?.git?.probeStatus ?? 'UNKNOWN',
            gaps: doctorJson.value.doctor.toolchain?.git?.gaps ?? [],
          }
        : { presence: 'UNAVAILABLE' },
    };
    console.error(JSON.stringify(details));
    assert.fail(`${label}: repository state was not observed; cannot assert CLEAN/DIRTY. Investigate GEF CLI Git executable trust/metadata diagnostics on this runner.`);
  }
  assert.equal(verdict.state, expectedState, `${label}: repository state did not match observed Git state.`);
  assert.equal(verdict.conflict, false, `${label}: GEF found repository conflict.`);
  return verdict;
}

function snapshotTree(path) {
  if (!existsSync(path)) return 'ABSENT';
  const root = path;
  const entries = [];
  function visit(current) {
    const info = lstatSync(current);
    const relative = current === root ? '.' : current.slice(root.length + 1).replaceAll('\\', '/');
    if (info.isSymbolicLink()) {
      entries.push([relative, 'SYMLINK', readlinkSync(current)]);
    } else if (info.isDirectory()) {
      entries.push([relative, 'DIRECTORY']);
      for (const name of readdirSync(current).sort()) visit(join(current, name));
    } else if (info.isFile()) {
      const digest = createHash('sha256').update(readFileSync(current)).digest('hex');
      entries.push([relative, 'FILE', digest]);
    } else {
      entries.push([relative, 'SPECIAL']);
    }
  }
  visit(root);
  return JSON.stringify(entries);
}

const version = run(['--version']);
assert.equal(version.exitCode, 0, `gef --version failed: ${version.stderr}`);
assert.match(version.stdout, /1\.1\.2/, 'The local CLI must report exactly version 1.1.2.');

const help = run(['--help']);
assert.equal(help.exitCode, 0, `gef --help failed: ${help.stderr}`);
for (const command of ['init', 'doctor', 'status']) {
  assert.ok(help.stdout.includes(command), `GEF help omits required command: ${command}`);
}

const before = gitStatus();
const gefBefore = snapshotTree(join(target, '.gef'));
const privateBefore = snapshotTree(join(target, '.gef-private'));
const doctor = run(['doctor', '--target', target, '--json']);
const doctorJson = parseJson('gef doctor', doctor);
assert.equal(doctor.exitCode, 0, `gef doctor failed: ${doctor.stderr}`);
assert.equal(doctorJson.ok, true, 'gef doctor did not return a successful observation.');
assert.equal(doctorJson.terminal, 'SUCCEEDED', 'gef doctor did not complete.');
assert.equal(doctorJson.value.effect, 'NONE', 'gef doctor must remain read-only.');
assert.equal(doctorJson.value.doctor.readOnly, true, 'gef doctor did not identify itself as read-only.');
const status = run(['status', '--target', target, '--json']);
const statusJson = parseJson('gef status', status);
assert.equal(status.exitCode, 0, `gef status failed: ${status.stderr}`);
assert.equal(statusJson.ok, true, 'gef status did not return a successful observation.');
assert.equal(statusJson.terminal, 'SUCCEEDED', 'gef status did not complete.');
assert.equal(statusJson.value.effect, 'NONE', 'gef status must remain read-only.');
assert.equal(statusJson.value.status.readOnly, true, 'gef status did not identify itself as read-only.');
const initPreview = run(['init', '--target', target, '--json']);
const initPreviewJson = parseJson('gef init preview', initPreview);
assert.equal(initPreview.exitCode, 0, `gef init preview failed: ${initPreview.stderr}`);
assert.equal(initPreviewJson.ok, true, 'gef init preview did not return a successful plan.');
assert.equal(initPreviewJson.terminal, 'SUCCEEDED', 'gef init preview did not complete.');
assert.equal(initPreviewJson.value.effect, 'NONE', 'gef init preview must remain read-only.');
assert.equal(initPreviewJson.value.plan.install.version, '1.1.2', 'GEF preview selected the wrong CLI version.');
assert.equal(initPreviewJson.value.plan.install.state, 'READY', 'GEF install plan is not ready.');
const expectedRepositoryState = before === '' ? 'CLEAN' : 'DIRTY';
requireObservedRepository('gef init preview', initPreviewJson.value.plan.repository, expectedRepositoryState);
assert.equal(initPreviewJson.value.plan.canonical.state, 'READY', 'GEF canonical source selection is not ready.');
assert.equal(initPreviewJson.value.plan.canonical.conflict, false, 'GEF preview found a canonical-source conflict.');
const after = gitStatus();
const gefAfter = snapshotTree(join(target, '.gef'));
const privateAfter = snapshotTree(join(target, '.gef-private'));

assert.equal(after, before, 'Read-only doctor/status/init preview changed the target Git state.');
assert.equal(gefAfter, gefBefore, 'Read-only doctor/status/init preview changed managed GEF state.');
assert.equal(privateAfter, privateBefore, 'Read-only doctor/status/init preview changed private transaction state.');

const ignoreProbe = spawnSync('git', ['check-ignore', '--quiet', '--no-index', '.gef-private/probe'], {
  cwd: target,
  encoding: 'utf8',
  timeout: 10_000,
  env: childEnvironment,
});
assert.ifError(ignoreProbe.error);
assert.equal(ignoreProbe.status, 0, '.gef-private is not ignored by the repository.');

console.log(JSON.stringify({
  result: 'PASS',
  version: '1.1.2',
  exitCodes: {
    version: version.exitCode,
    help: help.exitCode,
    doctor: doctor.exitCode,
    status: status.exitCode,
    initPreview: initPreview.exitCode,
  },
  diagnostics: {
    doctor: {
      exitCode: doctor.exitCode,
      securityDependency: doctorJson.value.doctor.security.dependency.state,
      securityGithub: doctorJson.value.doctor.security.github.state,
      governanceValid: doctorJson.value.doctor.governance.valid,
      governanceLimits: doctorJson.value.doctor.governance.observationLimits,
    },
    status: {
      exitCode: status.exitCode,
      repository: statusJson.value.status.repository.verdict?.state ?? 'UNAVAILABLE',
      repositoryObservationLimits: statusJson.value.status.repository.observationLimits,
      driftBaseline: statusJson.value.status.driftBaseline.state,
      drift: statusJson.value.status.drift,
      observationLimits: statusJson.value.status.observationLimits,
    },
    initPreview: {
      exitCode: initPreview.exitCode,
      version: initPreviewJson.value.plan.install.version,
      installState: initPreviewJson.value.plan.install.state,
      repository: initPreviewJson.value.plan.repository.verdict?.state ?? 'UNAVAILABLE',
      repositoryObservationLimits: initPreviewJson.value.plan.repository.observationLimits,
      canonical: initPreviewJson.value.plan.canonical.state,
      drift: initPreviewJson.value.plan.drift.class,
    },
  },
  targetUnchangedByReadOnlyCommands: true,
  privateStateIgnored: true,
}));
