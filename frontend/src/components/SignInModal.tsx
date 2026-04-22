import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Lock } from 'lucide-react';
import styles from './SignInModal.module.css';

interface SignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (token: string, userId: number) => void;
}

const SignInModal: React.FC<SignInModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    
    try {
      const res = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      onSuccess(data.access_token, data.user_id);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className={styles.overlay}>
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            transition={{ type: 'spring', damping: 25, stiffness: 300 }}
            className={styles.modal}
          >
            <button onClick={onClose} className={styles.closeButton}>
              <X size={20} />
            </button>

            <div className={styles.header}>
              <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
              <p>
                {isLogin ? 'Enter your credentials to access your agent.' : 'Sign up to start automating your workflow.'}
              </p>
            </div>

            <div className={styles.tabs}>
              <button
                onClick={() => setIsLogin(true)}
                className={`${styles.tab} ${isLogin ? styles.active : ''}`}
              >
                Login
              </button>
              <button
                onClick={() => setIsLogin(false)}
                className={`${styles.tab} ${!isLogin ? styles.active : ''}`}
              >
                Register
              </button>
            </div>

            <form onSubmit={handleSubmit} className={styles.form}>
              {error && <div className={styles.error}>{error}</div>}
              
              <div className={styles.inputGroup}>
                <Mail className={styles.inputIcon} size={18} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email address"
                  required
                  className={styles.input}
                />
              </div>

              <div className={styles.inputGroup}>
                <Lock className={styles.inputIcon} size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  required
                  className={styles.input}
                />
              </div>

              <button type="submit" disabled={loading} className={styles.submitBtn}>
                {loading ? 'Processing...' : isLogin ? 'Sign In' : 'Sign Up'}
              </button>
            </form>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default SignInModal;
