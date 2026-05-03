function errorHandler(err, req, res, next) {
  if (err.name === 'NotFoundError') return res.status(404).json({ error: err.message });
  if (err.name === 'ValidationError') return res.status(422).json({ error: err.message });
  if (err.name === 'AuthError') return res.status(401).json({ error: err.message });
  if (err.name === 'PaymentError') return res.status(400).json({ error: err.message });
  console.error('[ERROR]', err.message);
  res.status(500).json({ error: 'Internal server error' });
}

module.exports = errorHandler;
