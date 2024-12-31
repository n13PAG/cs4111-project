import { Text, View, Button, Alert, TextInput } from "react-native"
import { useForm, Controller } from "react-hook-form"
import React from 'react';
import {SafeAreaView, SafeAreaProvider} from 'react-native-safe-area-context';
import { yupResolver } from "@hookform/resolvers/yup"
import * as yup from "yup"
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
    const emailRegex = /@columbia.edu$/;
    const schema = yup
    .object({
        username: yup
            .string()
            .required('User name is required'),
        email: yup
            .string()
            .email('Invalid email')
            .required('Email is required')
            .matches(emailRegex, "Must a Columbia issued email"),
        password: yup
            .string()
            .required('No password provided.')
            .min(8, 'Password must contain at least 8 characters.')
    })

    const {
        control,
        handleSubmit,
        formState: {errors},
    } = useForm({
        resolver: yupResolver(schema),
        defaultValues: {
            email: '',
            username: '',
            password: '',
        }
    })

    const onPressSend = (formData:any) => {
        console.log(formData.username)
        console.log(formData.email)
        console.log(formData.password)

        fetch('http://127.0.0.1:8111/login_request', {
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
    };

    return (
        <View>
            <Text>Create an account</Text>
            <Controller
                control={control}
                rules={{
                    required: true,
                }}
                render={({field: {onChange, value}}) => (
                    <TextInput 
                        value={value}
                        onChange={onChange}
                        placeholder="Username"
                    />
                )}
                name="username"
            />
            <Controller
                control={control}
                rules={{
                    required: true,
                }}
                render={({field: {onChange, value}}) => (
                    <TextInput 
                        value={value}
                        onChange={onChange}
                        placeholder="Email"
                    />
                )}
                name="email"
            />
            {errors.email && <Text>{errors.email.message}</Text>}
            <Controller
                control={control}
                rules={{
                    required: true,
                }}
                render={({field: {onChange, value}}) => (
                    <TextInput 
                        value={value}
                        onChange={onChange}
                        placeholder="Password"
                    />
                )}
                name="password"
            />
            <Button 
                title="Submit"
                onPress={handleSubmit(onPressSend)} 
            />

            <HttpExample></HttpExample>
        </View>
    )
}