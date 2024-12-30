import { Text, View, Button, Alert } from "react-native"
import { useForm, Controller } from "react-hook-form"
import React from 'react';
import {SafeAreaView, SafeAreaProvider} from 'react-native-safe-area-context';
import { TextInput } from 'react-native-gesture-handler';
import BouncyCheckbox from "react-native-bouncy-checkbox";
import { Component } from "react";

class HttpExample extends Component {
    state = {
        data: ''
    }
    componentDidMount = () => {
        fetch('http://127.0.0.1:8111/testCourses', {
            method: 'GET'
        })
        .then((response) => response.json())
        .then((responseJson) => {
            console.log(responseJson)
            this.setState({
                data: responseJson
            })
        })
        .catch((error) => {
            console.error(error)
        })
    }

    render(): React.ReactNode {
        return (
            <View>
                <Text>{this.state.data.courses}</Text>
            </View>
        )
    }
}

export default function SignupScreen() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      email: "",
      uni: "",
      name: "",
      is_student: false,
    },
  })
  const onSubmit = (data:any) => console.log(data)

  return (
    <SafeAreaProvider>
        <SafeAreaView>
            <Controller
                control={control}
                rules={{
                required: true,
                }}
                render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                    placeholder="example@email.com"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                />
                )}
                name="email"
            />
            {/* {errors.email && <Text>This is required.</Text>} */}

            <Controller
                control={control}
                rules={{
                maxLength: 6,
                required: true,
                }}
                render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                    placeholder="UNI"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                />
                )}
                name="uni"
            />
            {/* {errors.uni[0] && errors.uni[1]} */}


            <Controller
                control={control}
                rules={{
                required: true,
                }}
                render={({ field: { onChange, onBlur, value } }) => (
                <TextInput
                    placeholder="Name"
                    onBlur={onBlur}
                    onChangeText={onChange}
                    value={value}
                />
                )}
                name="name"
            />
            {/* {errors.name && <Text>This is required.</Text>} */}

            {/* <Controller
                control={control}
                rules={{
                required: true,
                }}
                render={({ field: { onChange, onBlur, value } }) => (
                    <BouncyCheckbox onPress={(value: boolean) => {= true}} />
                )}
                name="is_student"
            /> */}

            <HttpExample></HttpExample>

            <Button title="Submit" onPress={handleSubmit(onSubmit)} />
        </SafeAreaView>
    </SafeAreaProvider>
    
  )
}