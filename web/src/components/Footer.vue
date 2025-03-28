<script setup>
import { Button, Dialog, InputText, Message } from 'primevue';
import { Form } from '@primevue/forms'
import { zodResolver } from '@primevue/forms/resolvers/zod';
import { z } from 'zod'
import { ref } from 'vue';
import { logout } from '../auth';
import { router } from '../router';
import { changePassword } from '../auth';
import { useToast } from 'primevue/usetoast';
const toast = useToast()
const resolver = ref(zodResolver(
    z.object({
        password: z.string()
            .min(8, "La password deve contenere almeno 8 caratteri")
            .refine(val => /[A-Z]/.test(val), "La password deve contenere almeno una lettera maiuscola")
            .refine(val => /[0-9]/.test(val), "La password deve contenere almeno un numero")
            .refine(val => /[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]/.test(val), "La password deve contenere almeno un carattere speciale")
    })
))

const changePasswordDialog = ref(false)

const logoutHandler = async () => {
    await logout()
    router.go("/setup")
}

const changePasswordHandler = async (data) => {
    if (!data.valid) {
        return
    }
    const result = await changePassword(data.values.password)

    if (result) {
        changePasswordDialog.value = false
        toast.add({ severity: 'success', summary: 'Password cambiata', detail: 'La password è stata cambiata con successo', life: 3000 })
    } else {
        toast.add({ severity: 'error', summary: 'Password non cambiata', detail: 'Errore durante il cambio password', life: 3000 })
    }
}
</script>
<template>
    <div class="flex items-center h-10 p-6 gap-2">
        <Button label="Logout" @click="logoutHandler" severity="secondary" size="small" text />
        <Button label="Cambia Password" @click="changePasswordDialog = true" severity="secondary" size="small" text />
    </div>
    <Dialog v-model:visible="changePasswordDialog" header="Cambia Password" modal class="w-full max-w-md">
        <span class="text-surface-500 dark:text-surface-400 block mb-8">Camia la password di amministratore.</span>
        <Form v-slot="$form" :initialValues="{ password: '' }" :resolver="resolver" @submit="changePasswordHandler">
            <div class="mb-4">
                <div class="flex items-center gap-4">
                    <label for="password" class="font-semibold w-24 flex-shrink-0">Password</label>
                    <InputText name="password" type="password" class="flex-auto" :invalid="$form.password?.invalid" />
                </div>
                <div class="mt-1 pl-[calc(theme(width.24)+theme(space.4))]">
                    <Message v-if="$form.password?.invalid" severity="error" size="small" variant="simple">
                        {{ $form.password.error.message }}
                    </Message>
                </div>
            </div>
            <div class="flex justify-end gap-2">
                <Button type="button" label="Annulla" severity="secondary" @click="changePasswordDialog = false" />
                <Button type="submit" label="Cambia" :disabled="$form.password?.invalid" />
            </div>
        </Form>
    </Dialog>
</template>