#!/bin/bash

LEVEL=99
INTERVAL=5
FAULTY_FANTRAY1=1
FAULTY_FANTRAY2=1
FAULTY_FANTRAY3=1

# FAN RPM Speed
IDLE=7000
LEVEL1=10000
LEVEL2=13000
LEVEL3=16000
LEVEL4=19000
LEVEL5=19000

I2C_ADAPTER="/sys/class/i2c-adapter/i2c-2/i2c-11"
SENSOR1="$I2C_ADAPTER/11-004c/hwmon/hwmon*/temp1_input"
SENSOR2="$I2C_ADAPTER/11-004d/hwmon/hwmon*/temp1_input"
SENSOR3="$I2C_ADAPTER/11-004e/hwmon/hwmon*/temp1_input"

# Three fan trays with each contains two separate fans
# fan1-fan4 fan2-fan5 fan3-fan6
FANTRAY1_FAN1=$I2C_ADAPTER/11-0029/fan1_target
FANTRAY1_FAN2=$I2C_ADAPTER/11-0029/fan2_target
FANTRAY2_FAN1=$I2C_ADAPTER/11-0029/fan3_target
FANTRAY2_FAN2=$I2C_ADAPTER/11-0029/fan4_target
FANTRAY3_FAN1=$I2C_ADAPTER/11-002a/fan1_target
FANTRAY3_FAN2=$I2C_ADAPTER/11-002a/fan2_target

FANTRAY1_FAN1_RPM=$I2C_ADAPTER/11-0029/fan1_input
FANTRAY1_FAN2_RPM=$I2C_ADAPTER/11-0029/fan2_input
FANTRAY2_FAN1_RPM=$I2C_ADAPTER/11-0029/fan3_input
FANTRAY2_FAN2_RPM=$I2C_ADAPTER/11-0029/fan4_input
FANTRAY3_FAN1_RPM=$I2C_ADAPTER/11-002a/fan1_input
FANTRAY3_FAN2_RPM=$I2C_ADAPTER/11-002a/fan2_input

function check_module
{
    MODULE=$1
    lsmod | grep "$MODULE" > /dev/null
    ret=$?
    if [[ $ret = "1" ]];  then
        echo "$MODULE is not loaded!"
        exit 1
    fi
}

function check_faulty_fan
{

    # Assume fans in FanTray spins less than 1000 RPM is faulty.
    # To Maintain temperature assign max speed 16200 RPM to all other fans.
    # This RPM speed handle temperature upto 75C degrees

    fan1=$(cat $FANTRAY1_FAN1_RPM)
    fan2=$(cat $FANTRAY1_FAN2_RPM)
    fan3=$(cat $FANTRAY2_FAN1_RPM)
    fan4=$(cat $FANTRAY2_FAN2_RPM)
    fan5=$(cat $FANTRAY3_FAN1_RPM)
    fan6=$(cat $FANTRAY3_FAN2_RPM)

    # FanTray1
    if [ "$fan1" -le "1000" ] || [ "$fan2" -le "1000" ]; then

        # First time detecting failure
        if [ $FAULTY_FANTRAY1 -lt "2" ]; then
            FAULTY_FANTRAY1=2
            /usr/local/bin/set-fan-speed 16200 2 > /dev/null
            logger "Faulty Fans in Fantray1 $fan1 $fan2 Please check."
        fi

    elif [ "$fan1" -ge "1000" ] || [ "$fan2" -ge "1000" ]; then
        FAULTY_FANTRAY1=0
    fi


    # FanTray2
    if [ "$fan3" -le "1000" ] || [ "$fan4" -le "1000" ]; then

        # First time detecting failure
        if [ $FAULTY_FANTRAY2 -lt "2" ]; then

            FAULTY_FANTRAY2=2
            /usr/local/bin/set-fan-speed 16200 2 > /dev/null
            logger "Faulty Fans in FanTray2: $fan3 $fan4. Please check."
        fi

    elif [ "$fan3" -ge "1000" ] || [ "$fan4" -ge "1000" ]; then
        FAULTY_FANTRAY2=0
    fi

    # FanTray3
    if [ "$fan5" -le "1000" ] || [ "$fan6" -le "1000" ]; then

        # First time detecting failure
        if [ $FAULTY_FANTRAY3 -lt "2" ]; then

            FAULTY_FANTRAY3=2
            /usr/local/bin/set-fan-speed 16200 2 > /dev/null
            logger "FanTray3 Fans are Faulty.. $fan5 $fan6. Please check."
        fi

    elif [ "$fan5" -ge "1000" ] || [ "$fan6" -ge "1000" ]; then

        FAULTY_FANTRAY3=0
    fi

}

function update_fan_speed
{
    local fan_speed=$1

    echo $fan_speed > $FANTRAY1_FAN1
    echo $fan_speed > $FANTRAY1_FAN2
    echo $fan_speed > $FANTRAY2_FAN1
    echo $fan_speed > $FANTRAY2_FAN2
    echo $fan_speed > $FANTRAY3_FAN1
    echo $fan_speed > $FANTRAY3_FAN2

}

function monitor_temp_sensors
{

    while true # go through all temp sensor outputs
    do
        sensor1=$(expr `echo $(cat $SENSOR1)` / 1000)
        sensor2=$(expr `echo $(cat $SENSOR2)` / 1000)
        sensor3=$(expr `echo $(cat $SENSOR3)` / 1000)
        sum=$(($sensor1 + $sensor2 + $sensor3))
        sensor_temp=$(($sum/3))

        if [ "$sensor_temp" -le "25" ] && [ "$LEVEL" -ne "0" ]
        then
            # Set Fan Speed to 7000 RPM"
            LEVEL=0
            update_fan_speed $IDLE
            logger "Adjusted FAN Speed to $IDLE RPM against $sensor_temp Temperature"

        elif [ "$sensor_temp" -ge "26" ] && [ "$sensor_temp" -le "44" ] && [ "$LEVEL" -ne "1" ]
        then
            # Set Fan Speed to 10000 RPM"
            LEVEL=1
            update_fan_speed $LEVEL1
            logger "Adjusted FAN Speed to $IDLE RPM against $sensor_temp Temperature"

        elif [ "$sensor_temp" -ge "45" ] && [ "$sensor_temp" -le "59" ] && [ "$LEVEL" -ne "2" ]
        then
            # Set Fan Speed to 13000 RPM"
            LEVEL=2
            update_fan_speed $LEVEL2
            logger "Adjusted FAN Speed to $IDLE RPM against $sensor_temp Temperature"

        elif [ "$sensor_temp" -ge "60" ] && [ "$sensor_temp" -le "79" ] && [ "$LEVEL" -ne "3" ]
        then
            # Set Fan Speed to 16000 RPM"
            LEVEL=3
            update_fan_speed $LEVEL3
            logger "Adjusted FAN Speed to $IDLE RPM against $sensor_temp Temperature"

        elif [ "$sensor_temp" -ge "80" ] && [ "$LEVEL" -ne "4" ]
        then
            # Set Fan Speed to 19000 RPM"
            LEVEL=4
            update_fan_speed $LEVEL4
            logger "Adjusted FAN Speed to $IDLE RPM against $sensor_temp Temperature"
        fi

    # Check for faulty fan
    check_faulty_fan

    done

}

# Check drivers for sysfs attributes
check_module "dell_s6000_platform"
check_module "max6620"

# main loop calling the main function at specified intervals
while true
do
    monitor_temp_sensors
    # Sleep while still handling signals
    sleep $INTERVAL &
    wait
done
