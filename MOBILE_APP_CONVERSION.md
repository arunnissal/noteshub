# 📱 NotesHub Mobile App Conversion Guide

## **Option 1: React Native (Recommended)**

### **Why React Native?**
- ✅ **True native performance**
- ✅ **App Store & Play Store distribution**
- ✅ **Push notifications**
- ✅ **Camera/file upload**
- ✅ **Offline support**
- ✅ **Single codebase for iOS & Android**

### **Step 1: Setup React Native Environment**

```bash
# Install Node.js (if not installed)
# Download from: https://nodejs.org/

# Install React Native CLI
npm install -g @react-native-community/cli

# Install Expo CLI (easier for beginners)
npm install -g @expo/cli
```

### **Step 2: Create React Native Project**

```bash
# Create new project
npx react-native init NotesHubMobile --template react-native-template-typescript

# OR use Expo (easier)
npx create-expo-app NotesHubMobile --template blank-typescript

cd NotesHubMobile
```

### **Step 3: Install Dependencies**

```bash
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs
npm install react-native-screens react-native-safe-area-context
npm install @react-native-async-storage/async-storage
npm install axios
npm install react-native-vector-icons
npm install react-native-paper
npm install react-native-image-picker
npm install react-native-gesture-handler
npm install react-native-reanimated
```

### **Step 4: Project Structure**

```
NotesHubMobile/
├── src/
│   ├── components/
│   │   ├── NoteCard.tsx
│   │   ├── SearchBar.tsx
│   │   ├── FilterModal.tsx
│   │   └── LoadingSpinner.tsx
│   ├── screens/
│   │   ├── HomeScreen.tsx
│   │   ├── LoginScreen.tsx
│   │   ├── RegisterScreen.tsx
│   │   ├── NoteDetailScreen.tsx
│   │   ├── AddNoteScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   ├── WishlistScreen.tsx
│   │   └── DashboardScreen.tsx
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── storage.ts
│   ├── navigation/
│   │   └── AppNavigator.tsx
│   └── utils/
│       ├── constants.ts
│       └── helpers.ts
├── App.tsx
└── package.json
```

### **Step 5: API Configuration**

Create `src/services/api.ts`:

```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'https://your-render-app.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add token to requests
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

### **Step 6: Authentication Service**

Create `src/services/auth.ts`:

```typescript
import api from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const authService = {
  async login(phone: string, password: string) {
    const response = await api.post('/login/', { phone, password });
    await AsyncStorage.setItem('access_token', response.data.tokens.access);
    await AsyncStorage.setItem('refresh_token', response.data.tokens.refresh);
    await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  async register(phone: string, password: string, name: string) {
    const response = await api.post('/register/', { phone, password, name });
    await AsyncStorage.setItem('access_token', response.data.tokens.access);
    await AsyncStorage.setItem('refresh_token', response.data.tokens.refresh);
    await AsyncStorage.setItem('user', JSON.stringify(response.data.user));
    return response.data;
  },

  async logout() {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
    await AsyncStorage.removeItem('user');
  },

  async isAuthenticated() {
    const token = await AsyncStorage.getItem('access_token');
    return !!token;
  }
};
```

### **Step 7: Main App Component**

Create `App.tsx`:

```typescript
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { Provider as PaperProvider } from 'react-native-paper';
import AppNavigator from './src/navigation/AppNavigator';

export default function App() {
  return (
    <PaperProvider>
      <NavigationContainer>
        <AppNavigator />
      </NavigationContainer>
    </PaperProvider>
  );
}
```

### **Step 8: Navigation Setup**

Create `src/navigation/AppNavigator.tsx`:

```typescript
import React from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import HomeScreen from '../screens/HomeScreen';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';
import NoteDetailScreen from '../screens/NoteDetailScreen';
import AddNoteScreen from '../screens/AddNoteScreen';
import ProfileScreen from '../screens/ProfileScreen';
import WishlistScreen from '../screens/WishlistScreen';
import DashboardScreen from '../screens/DashboardScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Wishlist" component={WishlistScreen} />
      <Tab.Screen name="Add Note" component={AddNoteScreen} />
      <Tab.Screen name="Dashboard" component={DashboardScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

export default function AppNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="Main" component={MainTabs} />
      <Stack.Screen name="NoteDetail" component={NoteDetailScreen} />
    </Stack.Navigator>
  );
}
```

### **Step 9: Sample Screen Implementation**

Create `src/screens/HomeScreen.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { Card, Title, Paragraph, Button } from 'react-native-paper';
import api from '../services/api';

interface Note {
  id: string;
  title: string;
  description: string;
  price: number;
  subject: { name: string };
  seller: { name: string };
}

export default function HomeScreen({ navigation }) {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchNotes = async () => {
    try {
      const response = await api.get('/notes/');
      setNotes(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchNotes();
  };

  const renderNote = ({ item }: { item: Note }) => (
    <Card style={styles.card} onPress={() => navigation.navigate('NoteDetail', { note: item })}>
      <Card.Content>
        <Title>{item.title}</Title>
        <Paragraph>{item.description.substring(0, 100)}...</Paragraph>
        <Text style={styles.subject}>{item.subject.name}</Text>
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
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
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

### **Step 10: Build and Test**

```bash
# For Android
npx react-native run-android

# For iOS (Mac only)
npx react-native run-ios

# Using Expo (easier)
npx expo start
```

### **Step 11: App Store Deployment**

#### **Android (Google Play Store)**
```bash
# Generate signed APK
cd android
./gradlew assembleRelease

# Or use Expo
npx expo build:android
```

#### **iOS (Apple App Store)**
```bash
# Using Expo
npx expo build:ios

# Or manual build with Xcode
```

---

## **Option 2: Flutter (Alternative)**

Flutter is Google's framework for building native apps:

```bash
# Install Flutter
# Download from: https://flutter.dev/docs/get-started/install

# Create Flutter project
flutter create noteshub_mobile
cd noteshub_mobile

# Run the app
flutter run
```

---

## **Option 3: Ionic (Hybrid App)**

Convert your existing HTML/CSS/JS:

```bash
# Install Ionic
npm install -g @ionic/cli

# Create Ionic project
ionic start noteshub-ionic blank --type=angular

# Add your existing HTML/CSS/JS
# Build for mobile
ionic capacitor add android
ionic capacitor add ios
```

---

## **🚀 RECOMMENDATION**

**Start with React Native** because:
- ✅ **Fastest to implement** (2-3 days)
- ✅ **Best performance**
- ✅ **Native features** (camera, push notifications)
- ✅ **App store ready**
- ✅ **Large community support**

**Your existing Django API will work perfectly with React Native!**

---

## **📋 Next Steps**

1. **Choose React Native** (recommended)
2. **Set up development environment**
3. **Create the mobile app structure**
4. **Connect to your existing API**
5. **Test on real devices**
6. **Deploy to app stores**

**Want me to help you start with React Native conversion?** 🚀 