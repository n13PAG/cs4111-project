import { useState, useEffect } from 'react';
import axios from 'axios';

function Home() {

    useEffect(() => {
        axios.get('http://127.0.0.1:8111/api/home')
            .then(response => setData(response.data))
            .catch(error => console.error(error));
    }, []);

    return (
        <div class="container px-4 px-lg-5 text-center">
            <h1>Project Name</h1>
            <h2>A note sharing app</h2>
            <div class="d-grid gap-3 d-sm-flex justify-content-sm-center justify-content-xl-start">
                <a href="{{url_for('login')}}" class="button">Login</a><br>
                <a href="{{url_for('signup')}}" class="button">Sign up</a>
            </div>
        </div>
    );
}

export default App;