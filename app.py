from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import os, uuid, subprocess, shutil

app = FastAPI()
BASE = "servers"
os.makedirs(BASE, exist_ok=True)

# ================= UI =================
@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<title>🔥 Pro Hosting Panel</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{margin:0;background:#0f172a;color:white;font-family:sans-serif}
.sidebar{width:220px;height:100vh;background:#020617;position:fixed;padding:20px}
.main{margin-left:240px;padding:20px}
button{padding:10px;margin:5px;background:#38bdf8;border:none;cursor:pointer}
.card{background:#1e293b;padding:15px;margin:10px 0;border-radius:10px}
#console{background:black;color:#0f0;height:200px;overflow:auto;padding:10px}
li{cursor:pointer}
</style>
</head>
<body>

<div class="sidebar">
<h2>⚡ Hosting</h2>
<button onclick="create()">+ Server</button>
<button onclick="del()">Delete</button>
</div>

<div class="main">
<h1>🚀 Hosting Panel</h1>

<div class="card">
<input type="file" id="f">
<button onclick="upload()">Upload</button>
<button onclick="run()">Run</button>
</div>

<div class="card">
<h3>📂 Files</h3>
<ul id="files"></ul>
</div>

<div class="card">
<h3>💻 Console</h3>
<pre id="console"></pre>
</div>
</div>

<script>
let sid=""
let currentFile=""

async function create(){
 let r=await fetch("/create",{method:"POST"})
 let d=await r.json()
 sid=d.id
 alert("Server: "+sid)
 load()
}

async function del(){
 await fetch("/delete/"+sid,{method:"DELETE"})
 alert("Deleted")
}

async function upload(){
 let f=document.getElementById("f").files[0]
 let fd=new FormData()
 fd.append("file",f)
 await fetch("/upload/"+sid,{method:"POST",body:fd})
 load()
}

async function load(){
 let r=await fetch("/list/"+sid)
 let d=await r.json()
 let ul=document.getElementById("files")
 ul.innerHTML=""
 d.files.forEach(x=>{
  ul.innerHTML+=`<li onclick="selectFile('${x}')">${x}</li>`
 })
}

function selectFile(f){
 currentFile=f
 alert("Selected: "+f)
}

async function run(){
 let r=await fetch("/run/"+sid+"/"+currentFile)
 let d=await r.json()
 document.getElementById("console").innerText=
 d.out+"\\n"+d.err
}
</script>

</body>
</html>
"""

# ================= API =================

@app.post("/create")
def create():
    sid=str(uuid.uuid4())
    os.makedirs(os.path.join(BASE,sid))
    return {"id":sid}

@app.get("/list/{sid}")
def list_files(sid:str):
    path=os.path.join(BASE,sid)
    return {"files":os.listdir(path)}

@app.post("/upload/{sid}")
async def upload(sid:str,file:UploadFile=File(...)):
    path=os.path.join(BASE,sid,file.filename)
    with open(path,"wb") as f:
        f.write(await file.read())
    return {"msg":"uploaded"}

@app.get("/run/{sid}/{file}")
def run(sid:str,file:str):
    path=os.path.join(BASE,sid,file)
    r=subprocess.run(["python3",path],capture_output=True,text=True)
    return {"out":r.stdout,"err":r.stderr}

@app.delete("/delete/{sid}")
def delete(sid:str):
    shutil.rmtree(os.path.join(BASE,sid),ignore_errors=True)
    return {"msg":"deleted"}