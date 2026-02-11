import axios from 'axios'

const demoApi = axios.create({
  baseURL: 'http://localhost:8000/api/v1/demo',
  headers: {
    'Content-Type': 'application/json'
  }
})

export default demoApi