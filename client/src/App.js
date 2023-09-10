import { useEffect, useRef } from 'react';

function App() {
  const websocket = useRef(null);

  function getWebSocketServer() {
    return "ws://localhost:8001/";
  }

  function init(websocket) {
    websocket.addEventListener("open", () => {
      // Send an "init" event according to who is connecting.
      const params = new URLSearchParams(window.location.search);
      let event = { type: "init" };

      if (params.has('join')) {
        const join_token = params.get('join');
        event['join'] = join_token;
      }

      websocket.send(JSON.stringify(event));
    });
  }

  function receiveHandler(websocket) {
    websocket.addEventListener("message", ({ data }) => {
      const event = JSON.parse(data);
      console.log(event);
    });
  }


  function send(obj, websocket) {
    websocket.send(JSON.stringify(obj));
  }

  function buttonClickHandler() {
    let input = document.getElementById('msg');
    let obj = {
      type: "message",
      message: input.value
    }
    send(obj, websocket.current);
  }

  useEffect(() => {
    // create a websocket
    websocket.current = new WebSocket(getWebSocketServer());

    // create a room or join a room when the websocket opens
    init(websocket.current);

    // listen for messages
    receiveHandler(websocket.current);
  }, [])

  return (
    <div>
      <label htmlFor="msg">Message</label>
      <input type="text" id="msg" />
      <button onClick={buttonClickHandler}>send</button>
    </div>
  );
}

export default App;
