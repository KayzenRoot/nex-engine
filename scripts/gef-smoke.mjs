import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

const target = process.cwd();
const cli = join(target, 'node_modules', '@gef-bootstrap', 'cli', 'bin', 'gef.mjs');

assert.ok(existsSync(cli), 'Local GEF CLI is missing; install the pinned package with npm ci.');

function run(args) {
  const result = spawnSync(process.execPath, [cli, ...args], {
    cwd: target,
    encoding: 'utf8',
    timeout: 30_000,
    env: { ...process.env, GIT_OPTIONAL_LOCKS: '0' },
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
    env: { ...process.env, GIT_OPTIONAL_LOCKS: '0' },
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

const version = run(['--version']);
assert.equal(version.exitCode, 0, `gef --version failed: ${version.stderr}`);
assert.match(version.stdout, /1\.1\.2/, 'The local CLI must report exactly version 1.1.2.');

const help = run(['--help']);
assert.equal(help.exitCode, 0, `gef --help failed: ${help.stderr}`);
for (const command of ['init', 'doctor', 'status']) {
  assert.ok(help.stdout.includes(command), `GEF help omits required command: ${command}`);
}

const before = gitStatus();
const doctor = run(['doctor', '--target', target, '--json']);
const doctorJson = parseJson('gef doctor', doctor);
const status = run(['status', '--target', target, '--json']);
const statusJson = parseJson('gef status', status);
const initPreview = run(['init', '--target', target, '--json']);
const initPreviewJson = parseJson('gef init preview', initPreview);
const after = gitStatus();

assert.equal(after, before, 'Read-only doctor/status/init preview changed the target Git state.');

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
  parsedJson: {
    doctorKeys: Object.keys(doctorJson ?? {}),
    statusKeys: Object.keys(statusJson ?? {}),
    initPreviewKeys: Object.keys(initPreviewJson ?? {}),
  },
  targetUnchangedByReadOnlyCommands: true,
}));
