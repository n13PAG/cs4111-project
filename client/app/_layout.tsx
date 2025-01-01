import { Stack } from "expo-router";
import { Slot } from 'expo-router';
import { SessionProvider } from './ctx';

export default function RootLayout() {
  return (
  <Stack>
    <SessionProvider>
      <Slot />
    <Stack.Screen name="index" />
    <Stack.Screen name="login" />
    <Stack.Screen name="signup" />
    </SessionProvider>
  </Stack>
);
}


