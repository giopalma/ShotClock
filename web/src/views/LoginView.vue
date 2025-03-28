<script setup>
import { Button, InputText, Message, Fieldset } from 'primevue'
import { Form } from '@primevue/forms';
import { z } from 'zod'
import { ref } from 'vue';
import { zodResolver } from '@primevue/forms/resolvers/zod';
import { useRoute } from 'vue-router';
import { router } from '../router';
import { login } from '../auth';
import { useToast } from 'primevue/usetoast';

const route = useRoute()
const toast = useToast()

const resolver = ref(zodResolver(
    z.object({
        password: z.string()
            .min(1, "La password non può essere vuota")
    })
))

const loginHandler = async (data) => {
    console.log(data)
    if (!data.valid) {
        return
    }
    const password = data.values.password
    const logged = await login(password)
    if (logged) {
        const redirectPath = route.query.redirect;
        if (redirectPath && typeof redirectPath === 'string') {
            console.log(`Redirecting back to: ${redirectPath}`);
            await router.replace(redirectPath);
        } else {
            console.log('No valid redirect path found, redirecting to /');
            await router.replace('/');
        }
    } else {
        toast.add({ severity: 'error', summary: 'Password non valida', detail: 'La password non è valida', life: 3000 })
        data.values.password = ''
    }
}
</script>

<template>
    <div class="flex flex-col items-center justify-center h-screen m-auto gap-4 max-w-md p-4">
        <h1 class="text-4xl font-bold text-[var(--p-emerald-600)]">Shot Clock</h1>
        <span class="text-sm text-gray-500">Accedi all'area di configurazione inserendo la password
            amministratore.</span>
        <Form v-slot="$form" :initialValues="{ password: '' }" :resolver="resolver" @submit="loginHandler"
            class="flex flex-col gap-4 w-full ">
            <div class="flex flex-col gap-2">
                <InputText name="password" type="password" placeholder="Password" fluid
                    :invalid="$form.password?.invalid" />
                <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">{{
                    $form.password.error.message }}</Message>
            </div>
            <Button label="Login" type="submit" severity="secondary" raised :disabled="!$form.valid" />
        </Form>
    </div>
</template>
