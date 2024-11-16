import { Button } from './components/ui/button';
import { MapPin } from 'lucide-react';
import WindSVG from './assets/wind-turbines-icon.svg';
import React from 'react';

function App() {
  const [location, setLocation] = React.useState('');
  const [socket, setSocket] = React.useState<WebSocket | null>(null);
  const [messages, setMessages] = React.useState<string[]>([]);

  React.useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      // Handle incoming messages
      setMessages((prevMessages: string[]) => [...prevMessages, event.data]);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    setSocket(ws);

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, []);

  const sendMessage = () => {
    if (socket && location) {
      socket.send(location);
      setLocation('');
    }
  };

  const handleInputChange = (event: any) => {
    setLocation(event.target.value); // Update state with input's value
  };

  return (
    <main className="font-geist text-black h-dvh w-full flex flex-col justify-center items-center gap-8">
      <img className="w-48" src={WindSVG} />
      <h1 className="text-4xl text-bold">Onshore Wind Development</h1>
      <div className="flex gap-2 items-center h-14 w-1/2 rounded-2xl border border-black bg-background px-4 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm">
        <MapPin />
        <input
          value={location}
          onChange={handleInputChange}
          className="placeholder:text-muted-foreground w-full py-2 focus:outline-none"
          placeholder="What is your project size and location?"
        ></input>
      </div>
      <Button onClick={sendMessage} className="text-lg">
        Get Resources
      </Button>
      <div className="h-20">
        {messages.map((message: string) => (
          <p>{message}</p>
        ))}
      </div>
    </main>
  );
}

export default App;
