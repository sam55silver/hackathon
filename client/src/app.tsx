import { Button } from './components/ui/button';
import { File } from 'lucide-react';
import WindSVG from './assets/wind-turbines-icon.svg';
import React from 'react';
import { Textarea } from './components/ui/textarea';

enum MessageType {
  user = 'User',
  agent = 'Agent',
  loading = 'Loading',
}

interface FileType {
  name: string;
  link: string;
}

interface Message {
  type: MessageType;
  content: string;
  files: null | FileType[];
}

function App() {
  const [query, setQuery] = React.useState('');
  const [messages, setMessages] = React.useState<Message[]>([]);

  const handleInputChange = (event: any) => {
    setQuery(event.target.value); // Update state with input's value
  };

  const sendMessage = () => {
    const userMsg = { type: MessageType.user, content: query, files: null };
    const loading = { type: MessageType.loading, content: '', files: null };
    setMessages([...messages, userMsg, loading]);
    setQuery('');

    fetch('http://localhost:8000/query_agent', {
      method: 'POST',
      body: JSON.stringify({ query }),
      headers: { 'Content-Type': 'application/json' },
    })
      .then((data) => data.json())
      .then((data) =>
        setMessages([
          ...messages,
          userMsg,
          { type: MessageType.agent, content: data.content, files: data.files },
        ])
      );
  };

  return (
    <main className="p-8 font-geist text-black min-h-dvh w-full flex flex-col justify-center items-center gap-8 container mx-auto">
      <div className="flex flex-row gap-2 items-end justify-center">
        <img className="w-32 pb-2" src={WindSVG} />
        <h2 className="text-7xl">👷‍♀️</h2>
      </div>
      <h1 className="text-3xl text-bold">Sustainable Developer Agent</h1>
      {messages.length != 0 ? (
        <div className="space-y-5 max-w-xl w-full">
          {messages.map((message: Message, id: number) => (
            <div key={id}>
              <div
                className={`text-sm w-fit bg-slate-200 rounded-md p-3 ${message.type == MessageType.user ? 'ml-auto' : ''}`}
              >
                <p className="font-semibold">{message.type}</p>
                <p className="mt-2">{message.content}</p>
              </div>
              {message.files != null ? (
                <div className="mt-2">
                  {message.files.map((file: FileType) => (
                    <div className="text-sm w-fit bg-slate-200 rounded-md p-3 flex flex-col justify-center items-center gap-2">
                      <File width={20} height={20} />
                      <a
                        className="text-primary underline"
                        href={`http://localhost:8000/download/${file.link}`}
                      >
                        {file.name}
                      </a>
                    </div>
                  ))}
                </div>
              ) : (
                <></>
              )}
            </div>
          ))}
        </div>
      ) : (
        <></>
      )}
      <div className="max-w-xl items-center flex flex-col gap-4 w-full">
        <Textarea
          value={query}
          placeholder="Ask any questions about onshore wind development in the Nova Scotia area."
          onChange={handleInputChange}
          className="border-black"
          rows={1}
        />
        <Button className="w-full" onClick={sendMessage}>
          Submit
        </Button>
      </div>
    </main>
  );
}

export default App;
