import { Button } from './components/ui/button';
import { MapPin } from 'lucide-react';
import WindSVG from './assets/wind-turbines-icon.svg';
import React from 'react';

function App() {
  const [location, setLocation] = React.useState('');

  const handleInputChange = (event: any) => {
    setLocation(event.target.value); // Update state with input's value
  };

  const submitLocation = () => {
    console.log('location:', location);
  };

  return (
    <main className="font-geist text-black h-dvh w-full flex flex-col justify-center items-center gap-8">
      <img className="w-48" src={WindSVG} />
      <h1 className="text-4xl text-bold">Where are you building?</h1>
      <div className="flex gap-2 items-center h-14 w-1/2 rounded-2xl border border-black bg-background px-4 py-2 text-base ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm">
        <MapPin />
        <input
          value={location}
          onChange={handleInputChange}
          className="placeholder:text-muted-foreground w-full py-2 focus:outline-none"
          placeholder="Enter the location of your development"
        ></input>
      </div>
      <Button onClick={submitLocation} className="text-lg">
        Get Resources
      </Button>
      <div className="h-20"></div>
    </main>
  );
}

export default App;
