import { replSend, replRawMode, ensureConnected, listFilesDevice } from 'monocle-node-cli';
import util from 'util';
import { exec } from 'child_process';

const enter = '\x1B[F\r';
const lineCharLimit = 19; // seems to be the limit per line
const execAsync = util.promisify(exec);

var lastLine = ""
async function sendLastLine() {
  const { stdout } = await execAsync('python iterm_last_line.py');
  if (lastLine != stdout) {
    lastLine = stdout;
    const textToPrint = lastLine.slice(-lineCharLimit);
    replSend(`import display; text = display.Text("${textToPrint}", 0, 200, display.WHITE, justify=display.MIDDLE_LEFT); display.show(text);` + enter);
  }
}

console.log("Connecting");
await ensureConnected();
console.log("Connected");
replSend("import device; device.battery_level();" + enter);
replSend("import led; led.off(led.RED);" + enter);

setInterval(sendLastLine, 1000);