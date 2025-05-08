// app/login/page.js
"use client";

import { useState } from 'react';
// Importa Link de next/link si necesitas un enlace (no hay en este login simple)
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = (event) => {
    event.preventDefault();
    setError(''); // Limpiar errores previos

    // --- Lógica de Autenticación Simulada ---
    // En un sistema real, enviarías username y password a tu API
    // fetch('/api/login', { ... })
    // .then(...)

    // Simulación simple: aceptar cualquier cosa y redirigir
    if (username && password) {
        console.log('Intentando login con:', { username, password });
        // Simulamos un login exitoso después de un pequeño retraso
        setTimeout(() => {
            alert('Login simulado exitoso!');
            router.push('/'); // Redirige al dashboard (página principal)
        }, 500);
    } else {
        setError('Por favor, ingrese usuario y contraseña.');
    }
    // --- Fin Lógica de Autenticación Simulada ---
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
              <label htmlFor="usernameInput" className="form-label">Usuario</label>
              <input
                type="text"
                className="form-control"
                id="usernameInput"
                placeholder="Ingrese usuario"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                maxLength="80"
              />
            </div>

            <div className="mb-3">
              <label htmlFor="passwordInput" className="form-label">Contraseña</label>
              <input
                type="password"
                className="form-control"
                id="passwordInput"
                placeholder="Contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                maxLength="255" /* Límite común para contraseñas, aunque el hash sea de 128 */
              />
            </div>

            <button type="submit" className="btn btn-primary w-100">Ingresar</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</div>

  );
}