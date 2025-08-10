import React, { useEffect, useState } from 'react';
import { io } from 'socket.io-client';

const socket = io();

export default function App(){
  const [conversations, setConversations] = useState([]);
  const [messages, setMessages] = useState([]);
  const [currentWa, setCurrentWa] = useState(null);
  const [text, setText] = useState("");

  const fetchConversations = async () => {
    const res = await fetch('/conversations');
    setConversations(await res.json());
  };
  const openChat = async (wa) => {
    setCurrentWa(wa);
    const res = await fetch('/messages/' + wa);
    setMessages(await res.json());
  };
  const sendMessage = async () => {
    if(!text || !currentWa) return;
    await fetch('/send', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({wa_id: currentWa, text})});
    setText("");
  };

  useEffect(()=>{
    fetchConversations();
    socket.on("new_message", msg => {
      if(msg.wa_id === currentWa) setMessages(m => [...m, msg]);
      fetchConversations();
    });
    socket.on("status_update", update => {
      setMessages(m => m.map(x => x._id === update.id ? {...x, status: update.status} : x));
    });
  }, [currentWa]);

  return (
    <div style={{display:"flex", height:"100vh"}}>
      <div style={{width:"300px", borderRight:"1px solid #ccc", overflowY:"auto"}}>
        {conversations.map(c=>(
          <div key={c._id} style={{padding:"10px", cursor:"pointer"}} onClick={()=>openChat(c._id)}>
            {c._id} ({c.count})
          </div>
        ))}
      </div>
      <div style={{flex:1, display:"flex", flexDirection:"column"}}>
        <div style={{flex:1, overflowY:"auto", padding:"10px"}}>
          {messages.map(m=>(
            <div key={m._id} style={{margin:"5px", padding:"8px", background:m.outgoing ? "#dcf8c6":"#fff"}}>
              {m.text} - <small>{m.status}</small>
            </div>
          ))}
        </div>
        <div style={{display:"flex", padding:"10px"}}>
          <input style={{flex:1}} value={text} onChange={e=>setText(e.target.value)} placeholder="Type a message" />
          <button onClick={sendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
}
