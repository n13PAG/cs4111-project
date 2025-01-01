import { Text, View, TextInput, Alert } from "react-native"
import { useForm, Controller } from "react-hook-form"
import * as React from 'react';
import {
  createStaticNavigation,
  useNavigation,
} from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Button } from '@react-navigation/elements';
//authentication flow: in server.py, there is an login object with user data, checks for user page access, user logn, page access-check
//route real quick, 

export default function App() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      EmailAddress: "",
      Password: "",
    },
  })
  const onSubmit = (data:any) => console.log(data)


    const navigation = useNavigation();
  
    
  

  return (
    <View>
      <Controller //this allows hooks to ctrl
        control={control}
        rules={{
          required: true,
          //may need to add email validation here?
        }}
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            placeholder="Email Address"
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
          />
        )}
        name="EmailAddress"
      />
      {errors.EmailAddress && <Text>This is required.</Text>}


      <Controller
        control={control}
        rules={{
          maxLength: 100,
          required:true,
        }}
        render={({ field: { onChange, onBlur, value } }) => (
          <TextInput
            placeholder="Password"
            onBlur={onBlur}
            onChangeText={onChange}
            value={value}
          />
        )}
        name="Password"
      />
      {errors.Password && <Text>This is required.</Text>}
      
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <Button onPress={() => navigation.navigate('signup')}>
            Login
        </Button>
      </View>

      
    </View>
  )
}