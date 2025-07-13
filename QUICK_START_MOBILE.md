# 🚀 Quick Start: Convert NotesHub to Mobile App

## **Step 1: Install Prerequisites**

```bash
# Install Node.js (if not already installed)
# Download from: https://nodejs.org/

# Install React Native CLI
npm install -g @react-native-community/cli

# Install Expo CLI (easier option)
npm install -g @expo/cli
```

## **Step 2: Create React Native Project**

```bash
# Navigate to your project directory
cd /c/Users/arunn/OneDrive/Desktop/notes

# Create React Native project
npx create-expo-app NotesHubMobile --template blank-typescript

# Navigate to the new project
cd NotesHubMobile
```

## **Step 3: Install Required Dependencies**

```bash
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context
npm install @react-native-async-storage/async-storage
npm install axios
npm install react-native-paper
npm install react-native-vector-icons
npm install expo-font
npm install expo-status-bar
```

## **Step 4: Replace App.tsx**

Replace the content of `App.tsx` with:

```typescript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { Provider as PaperProvider } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <PaperProvider>
      <NavigationContainer>
        <AppNavigator />
        <StatusBar style="auto" />
      </NavigationContainer>
    </PaperProvider>
  );
}
```

## **Step 5: Create Project Structure**

```bash
# Create directories
mkdir -p src/screens src/components src/services src/navigation src/utils

# Create basic files
touch src/services/api.ts
touch src/services/auth.ts
touch src/navigation/AppNavigator.tsx
touch src/screens/HomeScreen.tsx
touch src/screens/LoginScreen.tsx
```

## **Step 6: Configure API Connection**

Create `src/services/api.ts`:

```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Replace with your actual Render URL
const API_BASE_URL = 'https://your-render-app.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export default api;
```

## **Step 7: Create Basic Navigation**

Create `src/navigation/AppNavigator.tsx`:

```typescript
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/LoginScreen';

const Stack = createStackNavigator();

export default function AppNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Home" component={HomeScreen} />
    </Stack.Navigator>
  );
}
```

## **Step 8: Create Login Screen**

Create `src/screens/LoginScreen.tsx`:

```typescript
import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  Alert,
} from 'react-native';
import { TextInput, Button, Title, Text } from 'react-native-paper';
import api from '../services/auth';

export default function LoginScreen({ navigation }) {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!phone || !password) {
      Alert.alert('Error', 'Please fill all fields');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/login/', { phone, password });
      // Handle successful login
      navigation.navigate('Home');
    } catch (error) {
      Alert.alert('Error', 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Title style={styles.title}>NotesHub</Title>
      <Text style={styles.subtitle}>Login to your account</Text>
      
      <TextInput
        label="Phone Number"
        value={phone}
        onChangeText={setPhone}
        style={styles.input}
        keyboardType="phone-pad"
      />
      
      <TextInput
        label="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={styles.input}
      />
      
      <Button
        mode="contained"
        onPress={handleLogin}
        loading={loading}
        style={styles.button}
      >
        Login
      </Button>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 32,
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
  },
  input: {
    marginBottom: 15,
  },
  button: {
    marginTop: 10,
  },
});
```

## **Step 9: Create Home Screen**

Create `src/screens/HomeScreen.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import {
  View,
  FlatList,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { Card, Title, Paragraph, Text } from 'react-native-paper';
import api from '../services/api';

export default function HomeScreen() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const response = await api.get('/notes/');
      setNotes(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderNote = ({ item }) => (
    <Card style={styles.card}>
      <Card.Content>
        <Title>{item.title}</Title>
        <Paragraph>{item.description.substring(0, 100)}...</Paragraph>
        <Text style={styles.subject}>{item.subject?.name}</Text>
        <Text style={styles.price}>₹{item.price}</Text>
      </Card.Content>
    </Card>
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={notes}
        renderItem={renderNote}
        keyExtractor={(item) => item.id}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    margin: 8,
    elevation: 4,
  },
  subject: {
    color: '#666',
    fontSize: 14,
    marginTop: 4,
  },
  price: {
    color: '#2563eb',
    fontSize: 16,
    fontWeight: 'bold',
    marginTop: 4,
  },
  centered: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
```

## **Step 10: Test Your App**

```bash
# Start the development server
npx expo start

# This will open Expo DevTools in your browser
# You can:
# 1. Scan QR code with Expo Go app on your phone
# 2. Press 'a' for Android emulator
# 3. Press 'i' for iOS simulator (Mac only)
```

## **Step 11: Update API URL**

In `src/services/api.ts`, replace:
```typescript
const API_BASE_URL = 'https://your-render-app.onrender.com/api';
```

With your actual Render URL:
```typescript
const API_BASE_URL = 'https://your-actual-app-name.onrender.com/api';
```

## **🎉 You're Done!**

Your NotesHub mobile app is now running! You can:
- ✅ **Test on your phone** using Expo Go app
- ✅ **Add more screens** (Register, Profile, etc.)
- ✅ **Enhance the UI** with more components
- ✅ **Add features** like camera, file upload

## **Next Steps:**

1. **Test the basic app** - make sure login and notes display work
2. **Add more screens** - Register, Profile, Add Note, etc.
3. **Improve UI** - add icons, better styling
4. **Add features** - search, filters, wishlist
5. **Build for app stores** - generate APK/IPA files

**Your Django API will work perfectly with this React Native app!** 🚀

Need help with any specific screen or feature? 