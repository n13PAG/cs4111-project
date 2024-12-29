import {View, Text, StyleSheet, Button } from 'react-native';
import React from 'react';
import {SafeAreaView, SafeAreaProvider} from 'react-native-safe-area-context';
import { TextInput } from 'react-native-gesture-handler';

export default function SignupScreen() {
    const [email, onChangeEmail] = React.useState('example@email.com')
    const [password, onPasswordChange] = React.useState('')
    
    return (
        <SafeAreaProvider>
            <SafeAreaView>
                <TextInput 
                    onChangeText={onChangeEmail}
                    value={email}
                />
                <TextInput 
                    secureTextEntry={true}
                    onChangeText={onPasswordChange}
                    value={password}
                />
            </SafeAreaView>
        </SafeAreaProvider>

    )
}