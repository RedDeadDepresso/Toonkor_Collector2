import { MantineColorScheme } from '@mantine/core';

interface SettingsData {
  colorScheme: MantineColorScheme;
  displayEnglish: boolean;
  autoFetchToonkorUrl: boolean;
  toonkorUrl: string;
  setToonkorUrl: (value: string) => void;
  setAutoFetchToonkorUrl: (value: boolean) => void;
  setColorScheme: (value: MantineColorScheme) => void;
  setDisplayEnglish: (value: boolean) => void;
}

export default SettingsData;
