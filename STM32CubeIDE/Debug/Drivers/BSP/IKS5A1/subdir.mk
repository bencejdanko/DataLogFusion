################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (14.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_env_sensors.c \
C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.c \
C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_motion_sensors.c \
C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.c 

OBJS += \
./Drivers/BSP/IKS5A1/iks5a1_env_sensors.o \
./Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.o \
./Drivers/BSP/IKS5A1/iks5a1_motion_sensors.o \
./Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.o 

C_DEPS += \
./Drivers/BSP/IKS5A1/iks5a1_env_sensors.d \
./Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.d \
./Drivers/BSP/IKS5A1/iks5a1_motion_sensors.d \
./Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.d 


# Each subdirectory must supply rules for building sources it contributes
Drivers/BSP/IKS5A1/iks5a1_env_sensors.o: C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_env_sensors.c Drivers/BSP/IKS5A1/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F401xE -c -I../../Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../../../../../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../../../../../../Drivers/CMSIS/Include -I../../../../../../../Drivers/BSP/Components/ism330is -I../../../../../../../Drivers/BSP/Components/ism6hg256x -I../../../../../../../Drivers/BSP/Components/ilps22qs -I../../../../../../../Drivers/BSP/Components/iis2dulpx -I../../../../../../../Drivers/BSP/Components/iis2mdc -I../../../../../../../Drivers/BSP/IKS5A1 -I../../../../../../../Drivers/BSP/Components/Common -I../../../../../../../Middlewares/ST/STM32_MotionFX_Library/Inc -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"
Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.o: C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.c Drivers/BSP/IKS5A1/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F401xE -c -I../../Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../../../../../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../../../../../../Drivers/CMSIS/Include -I../../../../../../../Drivers/BSP/Components/ism330is -I../../../../../../../Drivers/BSP/Components/ism6hg256x -I../../../../../../../Drivers/BSP/Components/ilps22qs -I../../../../../../../Drivers/BSP/Components/iis2dulpx -I../../../../../../../Drivers/BSP/Components/iis2mdc -I../../../../../../../Drivers/BSP/IKS5A1 -I../../../../../../../Drivers/BSP/Components/Common -I../../../../../../../Middlewares/ST/STM32_MotionFX_Library/Inc -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"
Drivers/BSP/IKS5A1/iks5a1_motion_sensors.o: C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_motion_sensors.c Drivers/BSP/IKS5A1/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F401xE -c -I../../Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../../../../../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../../../../../../Drivers/CMSIS/Include -I../../../../../../../Drivers/BSP/Components/ism330is -I../../../../../../../Drivers/BSP/Components/ism6hg256x -I../../../../../../../Drivers/BSP/Components/ilps22qs -I../../../../../../../Drivers/BSP/Components/iis2dulpx -I../../../../../../../Drivers/BSP/Components/iis2mdc -I../../../../../../../Drivers/BSP/IKS5A1 -I../../../../../../../Drivers/BSP/Components/Common -I../../../../../../../Middlewares/ST/STM32_MotionFX_Library/Inc -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"
Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.o: C:/Users/bence/Downloads/x-cube-mems1/Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.c Drivers/BSP/IKS5A1/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F401xE -c -I../../Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc -I../../../../../../../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../../../../../../../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../../../../../../../Drivers/CMSIS/Include -I../../../../../../../Drivers/BSP/Components/ism330is -I../../../../../../../Drivers/BSP/Components/ism6hg256x -I../../../../../../../Drivers/BSP/Components/ilps22qs -I../../../../../../../Drivers/BSP/Components/iis2dulpx -I../../../../../../../Drivers/BSP/Components/iis2mdc -I../../../../../../../Drivers/BSP/IKS5A1 -I../../../../../../../Drivers/BSP/Components/Common -I../../../../../../../Middlewares/ST/STM32_MotionFX_Library/Inc -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Drivers-2f-BSP-2f-IKS5A1

clean-Drivers-2f-BSP-2f-IKS5A1:
	-$(RM) ./Drivers/BSP/IKS5A1/iks5a1_env_sensors.cyclo ./Drivers/BSP/IKS5A1/iks5a1_env_sensors.d ./Drivers/BSP/IKS5A1/iks5a1_env_sensors.o ./Drivers/BSP/IKS5A1/iks5a1_env_sensors.su ./Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.cyclo ./Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.d ./Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.o ./Drivers/BSP/IKS5A1/iks5a1_env_sensors_ex.su ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors.cyclo ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors.d ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors.o ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors.su ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.cyclo ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.d ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.o ./Drivers/BSP/IKS5A1/iks5a1_motion_sensors_ex.su

.PHONY: clean-Drivers-2f-BSP-2f-IKS5A1

