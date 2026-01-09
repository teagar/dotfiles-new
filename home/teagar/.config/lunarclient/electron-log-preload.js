
      try {
        (function V({contextBridge:J,ipcRenderer:K}){if(!K)return;K.on("__ELECTRON_LOG_IPC__",(ee,te)=>{window.postMessage({cmd:"message",...te})}),K.invoke("__ELECTRON_LOG__",{cmd:"getOptions"}).catch(ee=>console.error(new Error(`electron-log isn't initialized in the main process. Please call log.initialize() before. ${ee.message}`)));const $={sendToMain(ee){try{K.send("__ELECTRON_LOG__",ee)}catch(te){console.error("electronLog.sendToMain ",te,"data:",ee),K.send("__ELECTRON_LOG__",{cmd:"errorHandler",error:{message:te?.message,stack:te?.stack},errorName:"sendToMain"})}},log(...ee){$.sendToMain({data:ee,level:"info"})}};for(const ee of["error","warn","info","verbose","debug","silly"])$[ee]=(...te)=>$.sendToMain({data:te,level:ee});if(J&&process.contextIsolated)try{J.exposeInMainWorld("__electronLog",$)}catch{}typeof window=="object"?window.__electronLog=$:__electronLog=$})(require('electron'));
      } catch(e) {
        console.error(e);
      }
    