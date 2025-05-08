// app/login/page.js
"use client";

import { useState } from 'react';
// Importa Link de next/link si necesitas un enlace (no hay en este login simple)
import { useRouter } from 'next/navigation';
// Import the login function from your authService
import { login } from '../../services/authService'; // Adjust the path if necessary

export default function LoginPage() {
  const [identifier, setIdentifier] = useState(''); // Use 'identifier' as it can be username or email
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false); // State to manage loading state
  const router = useRouter();

  const handleSubmit = async (event) => { // Make the function async
    event.preventDefault();
    setError(''); // Clear previous errors
    setIsLoading(true); // Set loading state

    if (!identifier || !password) {
        setError('Por favor, ingrese usuario/email y contraseña.');
        setIsLoading(false);
        return;
    }

    try {
        // Call the login service
        const data = await login(identifier, password);

        console.log('Login successful:', data);
        // Handle successful login (e.g., store token if you implement JWT)
        // For now, just redirect
        alert('Login exitoso!'); // Use a more sophisticated notification in a real app
        router.push('/'); // Redirect to the dashboard (main page)

    } catch (err) {
        console.error('Login failed:', err);
        // Display error message from the API or a default message
        setError(err.message || 'Error al iniciar sesión. Intente de nuevo.');
    } finally {
        setIsLoading(false); // Clear loading state
    }
  };

  // Function to navigate to the registration page
  const handleGoToRegister = () => {
    router.push('/register');
  };

  return (
    <div className="container" style={{ minHeight: '80vh' }}>
      <div className="row justify-content-center align-items-center" style={{ minHeight: '100%' }}>
        <div className="col-12 col-sm-8 col-md-6 col-lg-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title text-center mb-4">Iniciar Sesión</h5>
              {error && <div className="alert alert-danger">{error}</div>}
              <form onSubmit={handleSubmit}>
                <div className="mb-3">
                  <label htmlFor="identifierInput" className="form-label">Usuario o Email</label>
                  <input
                    type="text"
                    className="form-control"
                    id="identifierInput"
                    placeholder="Ingrese su usuario o email" // Placeholder added
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    required
                    maxLength="120" // Adjust max length based on your DB schema (username 80, email 120)
                  />
                </div>

                <div className="mb-3">
                  <label htmlFor="passwordInput" className="form-label">Contraseña</label>
                  <input
                    type="password"
                    className="form-control"
                    id="passwordInput"
                    placeholder="Ingrese su contraseña" // Placeholder added
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    maxLength="255" /* Common limit for passwords, though the hash is 128 */
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-primary w-100"
                  disabled={isLoading} // Disable button while loading
                >
                  {isLoading ? 'Cargando...' : 'Ingresar'} {/* Button text changes based on loading state */}
                </button>
              </form>
               <div className="text-center mt-3">
                <p>¿No tienes una cuenta?</p>
                <button
                    className="btn btn-link"
                    onClick={handleGoToRegister} // Button to navigate to registration
                    disabled={isLoading} // Disable while loading login
                >
                    Registrarse aquí
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
