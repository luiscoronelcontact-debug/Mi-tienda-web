import { useEffect, useState } from 'react';
import { supabase } from '../supabase';

export default function ProfileView() {
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [province, setProvince] = useState('');
  const [city, setCity] = useState('');
  const [address, setAddress] = useState('');

  useEffect(() => {
    // Obtener la sesión activa compartida
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        getProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    // Escuchar cambios de sesión en tiempo real
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        getProfile(session.user.id);
      } else {
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  async function getProfile(userId) {
    try {
      setLoading(true);
      let { data, error } = await supabase
        .from('profiles')
        .select(`full_name, phone, province, city, address`)
        .eq('id', userId)
        .single();

      if (data) {
        setFullName(data.full_name || '');
        setPhone(data.phone || '');
        setProvince(data.province || '');
        setCity(data.city || '');
        setAddress(data.address || '');
      }
    } catch (error) {
      console.log('Error cargando el perfil:', error.message);
    } finally {
      setLoading(false);
    }
  }

  async function updateProfile(e) {
    e.preventDefault();
    if (!session) return;
    try {
      setLoading(true);
      const updates = {
        id: session.user.id,
        full_name: fullName,
        phone,
        province,
        city,
        address,
        updated_at: new Date(),
      };

      let { error } = await supabase.from('profiles').upsert(updates);
      if (error) throw error;
      alert('¡Perfil actualizado con éxito!');
    } catch (error) {
      alert('Error al actualizar el perfil');
    } finally {
      setLoading(false);
    }
  }

  if (!session) {
    return (
      <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow text-center">
        <p className="text-gray-700">Por favor, inicia sesión con Google para ver tu perfil.</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">Mi perfil</h2>
      <form onSubmit={updateProfile} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Nombre</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Teléfono</label>
          <input
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Provincia</label>
          <input
            type="text"
            value={province}
            onChange={(e) => setProvince(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Ciudad</label>
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700">Dirección</label>
          <input
            type="text"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            className="w-full p-2 border rounded"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-teal-600 text-white p-2 rounded hover:bg-teal-700"
        >
          {loading ? 'Guardando...' : 'Guardar cambios'}
        </button>
      </form>
    </div>
  );
}
