import { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
    const [data, setData] = useState(null);

    useEffect(() => {
        axios.get('http://127.0.0.1:8111/api/data')
            .then(response => setData(response.data))
            .catch(error => console.error(error));
    }, []);

    return (
        <div>
            <h1>React + Flask App</h1>
            {data ? <p>{data.message}</p> : <p>Loading...</p>}
        </div>
    );
}

export default App;