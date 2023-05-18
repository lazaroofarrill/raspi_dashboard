<template>
    <div class="text-center flex flex-col items-center gap-1">
        <h1 class="text-xl">Wind Speed Dashboard</h1>
        <h2>Fan {{ rangeValue > 0 ? 'enabled' : 'disabled' }}</h2>

        <div class="w-[200px]">
            <va-switch v-model="fansOn"></va-switch>
        </div>

        <div class="h-32"></div>
        <div class="flex flex-row bg-blue-accent-2 gap-64">
            <div>
                <div>Temperature</div>
                <div>{{ temperature }}</div>
                <div class="h-[200px]">
                    <va-slider readonly :max="70" vertical
                               v-model="temperature"></va-slider>
                </div>
            </div>
            <!--            <div>-->
            <!--                <div>Humidity</div>-->
            <!--                <div class="h-[200px]">-->
            <!--                    <va-slider readonly :max="100" vertical-->
            <!--                               v-model="humidity"></va-slider>-->
            <!--                </div>-->
            <!--            </div>-->
            <!--            <div>-->
            <!--                <div>Wind Speed</div>-->
            <!--                <div class="h-[200px]">-->
            <!--                    <va-slider readonly :max="100" vertical-->
            <!--                               v-model="windSpeed"></va-slider>-->
            <!--                </div>-->
            <!--            </div>-->

            <div>
                <div>Pressure</div>
                <div>{{ pressure }}</div>
                <div class="h-[200px]">
                    <va-slider readonly :max="200000" vertical
                               v-model="pressure"></va-slider>
                </div>
            </div>
        </div>

        <div></div>
    </div>
</template>

<script setup lang="ts">
import {ref, watch} from 'vue'

interface Readings {
    altitude: number
    sealevelPressure: number,
    pressure: number,
    temperature: number
}



const host = 'http://192.168.43.25:5000'
const readingsEndpoint = `${host}/readings`
const ledEndpoint = `${host}/led`
const toggleFanEndpoint = `${host}/fan`

const temperature = ref(0)
const pressure = ref(0)
const humidity = ref(0)
const windSpeed = ref(0)
const rangeValue = ref(0)
const fansOn = ref(false)

setInterval(async () => {
    const response = await fetch(readingsEndpoint)
    const body: Readings = await (response.json())
    temperature.value = body.temperature
    pressure.value = body.pressure
}, 1000)

watch(fansOn, async (newValue: boolean) => {
    console.log('toggling fan')
    const response = await fetch(`${toggleFanEndpoint}/${newValue ? 'on' : 'off'}`)
})

</script>
