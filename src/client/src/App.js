import React, { useState } from 'react';
import axios from 'axios';
import './index.css';
import stationNames from './dummyData';

function App() {
  const [stationName, setStationName] = useState('');
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const numOfPredictions = 7;

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await axios.post(`http://127.0.0.1:8000/mbajk/predict/${stationName}/${numOfPredictions}`);
      setPredictions(response.data.predictions);
      setLoading(false);
    } catch (error) {
      setError('Napaka pri pridobivanju podatkov.');
      setLoading(false);
    }
  };

  const handleStationChange = (e) => {
    setStationName(e.target.value);
  };

  return (
    <div className="container mx-auto my-5">
      <h1 className="text-3xl font-bold mb-4 bg-zinc-100 p-10">MBAJK- napovedovanje števila koles</h1>
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="flex items-center mb-4">
          <label htmlFor="stationName" className="mr-2">Izberite postajališče:</label>
          <select
            id="stationName"
            value={stationName}
            onChange={handleStationChange}
            className="border rounded py-1 px-2"
            required
          >
            <option value="">Izberite postajališče</option>
            {[...Array(29)].map((_, index) => (
              <option key={index} value={`station_${index + 1}`}>{stationNames[`station_${index + 1}`]}</option>
            ))}
          </select>
        </div>
        <button type="submit" className="bg-primaryRed text-white px-4 py-2 rounded disabled:bg-gray-400" disabled={loading}>
          {loading ? 'Nalaganje...' : 'Napovej'}
        </button>
      </form>
      {error && <div className="text-red-600 mb-4">{error}</div>}
      <div className="predictions">
        {predictions.length > 0 && (
          <div>
            <h2 className="text-xl font-bold mb-2">Napovedi za naslednjih {numOfPredictions} ur:</h2>
            <ul className="list-disc list-inside">
              {predictions.map((prediction, index) => (
                <li key={index} className="text-xl mb-1 font-bold">
                  Čez {index + 1}h: <span className="text-primaryRed font-black text-2xl">{prediction}</span>  🚲 na voljo
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
