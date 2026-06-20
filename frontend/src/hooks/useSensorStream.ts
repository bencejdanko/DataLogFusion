import { useState, useEffect } from 'react';

export interface SensorData {
  time: string;
  accelX: number;
  accelY: number;
  accelZ: number;
  gyroX: number;
  gyroY: number;
  gyroZ: number;
  magX: number;
  magY: number;
  magZ: number;
  pressure: number;
  temperature: number;
  pitch: number;
  roll: number;
}

export const useSensorStream = (isActive: boolean) => {
  const [dataStream, setDataStream] = useState<SensorData[]>([]);
  const [currentData, setCurrentData] = useState<SensorData | null>(null);
  const [isEmergency, setIsEmergency] = useState(false);

  useEffect(() => {
    if (!isActive) return;

    const source = new EventSource('http://localhost:8000/stream');

    source.onmessage = (e) => {
      try {
        const raw = JSON.parse(e.data);
        
        const nextPoint: SensorData = {
          time: raw.time || new Date().toLocaleTimeString(),
          accelX: raw.acc_x_mg || 0,
          accelY: raw.acc_y_mg || 0,
          accelZ: raw.acc_z_mg || 0,
          gyroX: raw.gyr_x_mdps || 0,
          gyroY: raw.gyr_y_mdps || 0,
          gyroZ: raw.gyr_z_mdps || 0,
          magX: raw.mag_x_mgauss || 0,
          magY: raw.mag_y_mgauss || 0,
          magZ: raw.mag_z_mgauss || 0,
          pressure: raw.press_hpa || 0,
          temperature: Number(raw.temp || raw.temperature) || 0,
          pitch: raw.pitch_deg || 0,
          roll: raw.roll_deg || 0,
        };

        // Emergency logic: Z-axis gyro exceeds threshold (e.g. > 8000 mdps) or Z accel drops (< 500 mg, indicating freefall/tilt)
        if (Math.abs(nextPoint.gyroZ) > 8000 || Math.abs(nextPoint.accelZ) < 500) {
          setIsEmergency(true);
        }

        setCurrentData(nextPoint);
        setDataStream((prev) => {
          const newStream = [...prev, nextPoint];
          // Keep last 50 points for chart
          if (newStream.length > 50) return newStream.slice(newStream.length - 50);
          return newStream;
        });
      } catch (err) {
        console.error("Error parsing SSE data:", err);
      }
    };

    source.onerror = (err) => {
      console.error("SSE connection error:", err);
    };

    return () => {
      source.close();
    };
  }, [isActive]);

  const resetEmergency = () => {
    setIsEmergency(false);
  };

  return { dataStream, currentData, isEmergency, resetEmergency };
};
