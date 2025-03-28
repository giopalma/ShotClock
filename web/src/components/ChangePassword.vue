<script setup>
import { zodResolver } from '@primevue/forms/resolvers/zod';
import { z } from 'zod'
import { ref } from 'vue';

const resolver = ref(zodResolver(
    z.object({
        password: z.string()
            .min(8, "La password deve contenere almeno 8 caratteri")
            .refine(val => /[A-Z]/.test(val), "La password deve contenere almeno una lettera maiuscola")
            .refine(val => /[0-9]/.test(val), "La password deve contenere almeno un numero")
            .refine(val => /[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]/.test(val), "La password deve contenere almeno un carattere speciale")
    })
))


</script>

<template>

</template>
