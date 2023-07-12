// capture display
let maxHistory = 1000;
const history = [];
const historyControls = {
    slider: document.getElementById('historySlider'),
    previousButton: document.getElementById('historyPrevious'),
    nextButton: document.getElementById('historyNext'),
    index: 0,
    back: false,
    forwards: false,
    slowmode: false,
    quickmode: false,
    maxSize: 5000
};
const fpsTimes = [];
let fps = 0;
const fpsDisplay = document.getElementById('fps');
const display0Img = document.getElementById('display0Img');
const display1Img = document.getElementById('display1Img');
function addCapture(images) {
    history.unshift({
        type: 0,
        images: [
            'data:image/jpeg;base64,' + images[0],
            'data:image/jpeg;base64,' + images[1]
        ],
        fps: fps
    });
    if (history.length > historyControls.maxSize) history.pop();
    let scrollWith = historyControls.slider.value == historyControls.slider.max;
    historyControls.slider.max = history.length;
    if (scrollWith) {
        historyControls.slider.value = history.length;
        display();
    }
    fpsTimes.push(performance.now());
};
function addData(data) {
    history.unshift({
        type: 1,
        images: [
            'data:image/jpeg;base64,' + images[0],
            'data:image/jpeg;base64,' + images[1]
        ],
        distances: [],
        pos: [],
        landmarks: [],
        fps: fps
    });
    if (history.length > historyControls.maxSize) history.pop();
    let scrollWith = historyControls.slider.value == historyControls.slider.max;
    historyControls.slider.max = history.length;
    if (scrollWith) {
        historyControls.slider.value = history.length;
        display();
    }
    fpsTimes.push(performance.now());
};
function display() {
    const data = history[historyControls.index];
    display0Img.src = data.images[0];
    display1Img.src = data.images[1];
    if (data.type == 1) {
        // stuff
    }
};

// controls
historyControls.slider.oninput = (e) => {
    historyControls.index = history.length - parseInt(historyControls.slider.value);
    display();
};
historyControls.nextButton.onclick = (e) => {
    historyControls.index = Math.max(0, historyControls.index - 1);
    historyControls.slider.value = history.length - historyControls.index;
    display();
};
historyControls.previousButton.onclick = (e) => {
    historyControls.index = Math.min(history.length - 1, historyControls.index + 1);
    historyControls.slider.value = history.length - historyControls.index;
    display();
};
function downloadFrame() {
    const downloadCanvas = document.createElement('canvas');
    downloadCanvas.width = 272;
    downloadCanvas.height = 154;
    const downloadctx = downloadCanvas.getContext('2d');
    downloadctx.drawImage(displayImg, 0, 0);
    downloadctx.drawImage(canvas, 0, 0);
    downloadctx.drawImage(canvas2, 0, 0);
    // set data
    let data = downloadCanvas.toDataURL('image/png');
    const a = document.createElement('a');
    a.href = data;
    let current = new Date();
    a.download = `SPARK-img_${current.getHours()}-${current.getMinutes()}_${current.getMonth()}-${current.getDay()}-${current.getFullYear()}.png`;
    a.click();
};
function downloadSession() {
    // data...
    const data = 'data:text/json;charset=UTF-8,' + encodeURIComponent(JSON.stringify(history));
    const a = document.createElement('a');
    a.href = data;
    let current = new Date();
    a.download = `SPARK-data_${current.getHours()}-${current.getMinutes()}_${current.getMonth()}-${current.getDay()}-${current.getFullYear()}.json`;
    a.click();
};
function importSession() {
    // create file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.click();
    input.oninput = () => {
        // read files
        let files = input.files;
        if (files.length == 0) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            // set history
            let raw = JSON.parse(e.target.result);
            history.splice(0, history.length);
            for (let i in raw) {
                history.push(raw[i]);
            }
            historySlider.max = 0;
            displayChange();
        };
        reader.readAsText(files[0]);
    };
};
setInterval(() => {
    while (performance.now() - fpsTimes[0] > 1000) fpsTimes.shift();
    fps = fpsTimes.length;
    fpsDisplay.innerText = 'FPS: ' + fps;
}, 50);
document.addEventListener('keydown', (e) => {
    if (e.key == 'ArrowLeft') {
        historyControls.back = true;
    } else if (e.key == 'ArrowRight') {
        historyControls.forwards = true;
    } else if (e.key == 'Control') {
        historyControls.quickmode = true;
    } else if (e.key == 'Shift') {
        historyControls.slowmode = true;
    } else if (e.key.toLowerCase() == 's' && e.ctrlKey) {
        downloadSession();
        e.preventDefault();
    } else if (e.key.toLowerCase() == 'o' && e.ctrlKey) {
        importSession();
        e.preventDefault();
    }
});
document.addEventListener('keyup', (e) => {
    if (e.key == 'ArrowLeft') {
        historyControls.back = false;
    } else if (e.key == 'ArrowRight') {
        historyControls.forwards = false;
    } else if (e.key == 'Control') {
        historyControls.quickmode = false;
    } else if (e.key == 'Shift') {
        historyControls.slowmode = false;
    }
});
historyControls.slider.onkeydown = (e) => {
    historyControls.slider.blur()
};
let timer = 0;
setInterval(() => {
    timer = (timer + 1) % 8;
    if (historyControls.slowmode && timer % 8 != 0) return;
    if (!historyControls.quickmode && timer % 4 != 0) return;
    if (historyControls.back) historyControls.previousButton.onclick();
    if (historyControls.forwards) historyControls.nextButton.onclick();
}, 25);
socket.on('capture', addCapture); // 0 is jpeg, 1 is png
socket.on('data', () => 'idk');

// controls 2: electric boogaloo
const modSave = document.getElementById('modSave');
const modFilter = document.getElementById('modFilter');
const stream = document.getElementById('stream');
const capture = document.getElementById('capture');
const rawcapture = document.getElementById('rawCapture');
const streamToggle = document.getElementById('streamToggle');
socket.on('streamState', (state) => {
    streamToggle.checked = state[0];
    modFilter.checked = state[1];
    modSave.checked = state[2];
    if (streamToggle.checked) {
        stream.style.backgroundColor = 'red';
        stream.innerText = 'STOP STREAM';
        modFilter.disabled = true;
        modSave.disabled = true;
    } else {
        stream.style.backgroundColor = '';
        stream.innerText = 'START STREAM';
        modFilter.disabled = false;
        modSave.disabled = false;
    }
});
stream.onclick = () => {
    streamToggle.checked = !streamToggle.checked;
    socket.emit('stream', { save: modSave.checked, filter: modFilter.checked, colors: getColors() });
};
capture.onclick = () => {
    socket.emit('capture', { save: modSave.checked, filter: modFilter.checked, colors: getColors() });
};
rawcapture.onclick = () => {
    socket.emit('rawCapture');
};
stream.disabled = true;
capture.disabled = true;
rawcapture.disabled = true;