import { Button } from './components/ui/button';
import { File, Link } from 'lucide-react';
import WindSVG from './assets/wind-turbines-icon.svg';
import React from 'react';
import { Textarea } from './components/ui/textarea';

enum MessageType {
  user = 'User',
  agent = 'Agent',
  loading = 'Loading',
}

enum SourceType {
  file = 'file',
  link = 'link',
}

interface Source {
  name: string;
  link: string;
  type: SourceType;
}

interface Message {
  type: MessageType;
  content: string;
  sources: null | Source[];
}

function App() {
  const [query, setQuery] = React.useState('');
  const [messages, setMessages] = React.useState<Message[]>([]);

  const handleInputChange = (event: any) => {
    setQuery(event.target.value); // Update state with input's value
  };

  const sendMessage = () => {
    const userMsg = { type: MessageType.user, content: query, sources: null };
    const loading = { type: MessageType.loading, content: '', sources: null };
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
          {
            type: MessageType.agent,
            content: data.content,
            sources: data.sources,
          },
        ])
      );
  };

  React.useEffect(() => console.log(messages), [messages]);

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
              {message.sources != null ? (
                <div className="mt-2 space-y-2">
                  {message.sources.map((source: Source) => (
                    <div className="text-sm w-fit bg-slate-200 rounded-md p-3 flex flex-row justify-center items-center gap-2">
                      {source.type == SourceType.file ? (
                        <>
                          <File width={20} height={20} />
                          <a
                            className="text-primary underline"
                            href={`http://localhost:8000/download/${source.link}`}
                          >
                            {source.name}
                          </a>
                        </>
                      ) : (
                        <>
                          <Link width={20} height={20} />
                          <a
                            className="text-primary underline"
                            href={source.link}
                          >
                            {source.name}
                          </a>
                        </>
                      )}
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
