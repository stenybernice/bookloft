import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchDemoUsers } from '../services/api';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [demoUsers, setDemoUsers] = useState([]);
  const [activeUser, setActiveUser] = useState({
    user_id: 99999,
    name: 'Aria Vance (New Reader)',
    persona: 'New Reader',
    location: 'New York, NY, USA',
    age: 24,
    rating_count: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDemoUsers = async () => {
      try {
        const users = await fetchDemoUsers();
        setDemoUsers(users);
        if (users && users.length > 0) {
          // Default to the new reader or first demo user
          const coldUser = users.find(u => u.user_id === 99999) || users[0];
          setActiveUser(coldUser);
        }
      } catch (err) {
        console.error('Failed to fetch demo users:', err);
      } finally {
        setLoading(false);
      }
    };

    loadDemoUsers();
  }, []);

  const switchUser = (userId) => {
    const found = demoUsers.find(u => u.user_id === parseInt(userId, 10));
    if (found) {
      setActiveUser(found);
    }
  };

  const updateUserRatingCount = (newCount) => {
    setActiveUser(prev => ({
      ...prev,
      rating_count: newCount
    }));
  };

  return (
    <UserContext.Provider value={{ activeUser, demoUsers, switchUser, updateUserRatingCount, loading }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => useContext(UserContext);
