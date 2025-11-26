const axios = require('axios');
const FormData = require('form-data');

const api = axios.create({
  baseURL: 'http://httpbin.org',
  headers: {
    'Content-Type': 'application/json',
  },
});

async function testUpload() {
  const formData = new FormData();
  formData.append('test', 'value');

  try {
    console.log('Sending request...');
    const response = await api.post('/post', formData, {
        headers: {
            'Content-Type': undefined
        }
    });
    console.log('Response headers:', response.config.headers);
    console.log('Request Content-Type sent:', response.request.getHeader ? response.request.getHeader('content-type') : 'unknown');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

testUpload();
