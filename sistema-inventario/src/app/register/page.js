// app/register/page.js
"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
// Import the register function from your authService
import { register } from '../../services/authService'; // Adjust the path if necessary

export default function RegisterPage() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState(''); // State for success message
  const [isLoading, setIsLoading] = useState(false); // State to manage loading state
  const router = useRouter();

  const handleSubmit = async (event) => { // Make the function async
    event.preventDefault();
    setError(''); // Clear previous errors
    setSuccessMessage(''); // Clear previous success messages
    setIsLoading(true); // Set loading state

    // Basic client-side validation
    if (!username || !password) {
        setError('El nombre de usuario y la contraseña son obligatorios.');
        setIsLoading(false);
        return;
    }

    if (password.length < 6) { // Match the minimum length check in your service
        setError('La contraseña debe tener al menos 6 caracteres.');
        setIsLoading(false);
        return;
    }

    // Optional: Basic email format validation
    if (email && !/\S+@\S+\.\S+/.test(email)) {
        setError('Formato de email inválido.');
        setIsLoading(false);
        return;
    }


    try {
        // Call the register service
        const data = await register({
            username: username,
            email: email || null, // Send null if email is empty
            password: password
        });

        console.log('Registration successful:', data);
        setSuccessMessage('¡Registro exitoso! Ahora puedes iniciar sesión.');
        // Optionally clear the form or redirect after success
        setUsername('');
        setEmail('');
        setPassword('');
        // router.push('/login'); // Uncomment to automatically redirect to login after successful registration

    } catch (err) {
        console.error('Registration failed:', err);
        // Display error message from the API or a default message
        setError(err.message || 'Error al registrar usuario. Intente de nuevo.');
    } finally {
        setIsLoading(false); // Clear loading state
    }
  };

   // Function to navigate back to the login page
  const handleGoToLogin = () => {
    router.push('/login');
  };


  return (
    <div className="container" style={{ minHeight: '80vh' }}>
      <div className="row justify-content-center align-items-center" style={{ minHeight: '100%' }}>
        <div className="col-12 col-sm-8 col-md-6 col-lg-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title text-center mb-4">Registrarse</h5>
              {error && <div className="alert alert-danger">{error}</div>}
              {successMessage && <div className="alert alert-success">{successMessage}</div>}
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="usernameInput" className="form-label">Nombre de Usuario</label>
                  <input
                    type="text"
                    className="form-control"
                    id="usernameInput"
                    placeholder="Ingrese un nombre de usuario" // Placeholder added
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    maxLength="80" // Match your DB schema
                  />
                </div>

                <div className="mb-3">
                  <label htmlFor="emailInput" className="form-label">Email (Opcional)</label>
                  <input
                    type="email" // Use type="email" for better mobile keyboards and basic browser validation
                    className="form-control"
                    id="emailInput"
                    placeholder="Ingrese su email (opcional)" // Placeholder added
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    maxLength="120" // Match your DB schema
                  />
                </div>

                <div className="mb-3">
                  <label htmlFor="passwordInput" className="form-label">Contraseña</label>
                  <input
                    type="password"
                    className="form-control"
                    id="passwordInput"
                    placeholder="Cree una contraseña (mín. 6 caracteres)" // Placeholder added
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    minLength="6" // Add client-side minLength
                    maxLength="255"
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100"
                  disabled={isLoading} // Disable button while loading
                >
                  {isLoading ? 'Registrando...' : 'Registrarse'} {/* Button text changes */}
                </button>
              </form>
               <div className="text-center mt-3">
                <p>¿Ya tienes una cuenta?</p>
                <button
                    className="btn btn-link"
                    onClick={handleGoToLogin} // Button to navigate back to login
                     disabled={isLoading} // Disable while loading registration
                >
                    Iniciar sesión aquí
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
