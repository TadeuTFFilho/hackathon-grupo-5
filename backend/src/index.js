require('dotenv').config();
const express = require('express');
const cors = require('cors');

const debtRoutes = require('./routes/debts');

const app = express();
app.use(cors());
app.use(express.json());

app.get('/health', (req, res) => res.json({ status: 'ok' }));
app.use('/api/debts', debtRoutes);

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`🚀 Backend rodando em http://localhost:${PORT}`));
