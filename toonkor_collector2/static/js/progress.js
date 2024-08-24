const progressSocket = new WebSocket('ws://' + window.location.host + '/ws/progress/');

progressSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const progress = (data.current / data.total) * 100;
    document.getElementById('progress-bar').style.width = progress + '%';
};

progressSocket.onclose = function(e) {
    console.error('WebSocket closed unexpectedly');
};