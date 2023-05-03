import { replSend, replRawMode, ensureConnected, listFilesDevice } from 'monocle-node-cli';
import util from 'util';
import { exec } from 'child_process';
import { promises as fs } from 'fs';

const execAsync = util.promisify(exec);
const enter = '\x1B[F\r';
const lineCharLimit = 24;
const displayAPI = await fs.readFile('wip_display.py', 'utf8');
const lineLimit = 6;
var lineBuffer = new Array(lineLimit);
lineBuffer.fill(".");
var lastLine = ""

// From: https://stackoverflow.com/a/63558697/1960938
const isNilOrWhitespace = input => (input?.trim()?.length || 0) === 0;
function stringWithPlaceholder(string) {
  if (isNilOrWhitespace(string)) {
    return ".";
  }
  return string;
}

async function sendLastLine() {
  const { stdout } = await execAsync('python iterm_last_line.py 0');
  if (lastLine != stdout) {
    lastLine = stdout;
    lineBuffer.shift();
    lineBuffer.push(lastLine.slice(-lineCharLimit));

    var replCommmand = `import display;`;
    replCommmand += `t1 = display.Text("${stringWithPlaceholder(lineBuffer[5])}", 10, 10, display.GREEN);`;
    replCommmand += `t2 = display.Text("${stringWithPlaceholder(lineBuffer[4])}", 10, 80, display.GREEN);`;
    replCommmand += `t3 = display.Text("${stringWithPlaceholder(lineBuffer[3])}", 10, 150, display.GREEN);`;
    replCommmand += `t4 = display.Text("${stringWithPlaceholder(lineBuffer[2])}", 10, 220, display.GREEN);`;
    replCommmand += `t5 = display.Text("${stringWithPlaceholder(lineBuffer[1])}", 10, 290, display.GREEN);`;
    replCommmand += `t6 = display.Text("${stringWithPlaceholder(lineBuffer[0])}", 10, 360, display.GREEN);`;
    replCommmand += `display.show(t1, t2, t3, t4, t5, t6)`;
    replSend(replCommmand + enter);
  }
}

console.log("Connecting");
await ensureConnected();
console.log("Connected");

replSend("import device; device.battery_level();" + enter);
replSend("import led; led.off(led.RED);" + enter);
// replSend("import display; display.brightness(4);" + enter);
replSend('\x05' + displayAPI + '\x04');

setInterval(sendLastLine, 500);