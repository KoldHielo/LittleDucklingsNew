// --- VALIDATION FUNCTIONS ---

const isValidEmail = (email) => {
  const trimmed = email.trim().toLowerCase();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(trimmed);
};

const isValidPhone = (phone) => {
  // Remove spaces, dashes, parentheses, etc.
  const cleanPhone = phone.trim().replace(/[^\d+]/g, '');
  // Basic E.164 format: + followed by 10–15 digits
  return /^\+\d{10,15}$/.test(cleanPhone);
};

const validatePasswords = (password, confirmPassword) => {
  if (password !== confirmPassword) return false;
  const strongPwdRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^])[A-Za-z\d@$!%*?&#^]{8,}$/;
  return strongPwdRegex.test(password);
};

// --- TRIMMING / CLEANING FUNCTIONS ---

const trimWhitespace = (value) => value.trim().replace(/\s+/g, ' ');

const trimName = (value) => {
  return trimWhitespace(value)
    .split(' ')
    .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
    .join(' ');
};

const cleanEmail = (email) => email.trim().toLowerCase();

const cleanPhone = (phone) => phone.trim().replace(/[^\d+]/g, '');