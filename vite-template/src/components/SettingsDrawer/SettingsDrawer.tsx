import { SettingsContext } from '@/contexts/SettingsContext';
import { Button, Drawer, Group, Switch, Title } from '@mantine/core';
import { useContext, useState } from 'react';
import { TextInput } from '@mantine/core';
import { useInputState } from '@mantine/hooks';

interface settingsDrawerPros {
  settingsOpened: boolean;
  closeSettings: () => void;
} 


const SettingsDrawer = ({ settingsOpened, closeSettings }: settingsDrawerPros) => {
  const { displayEnglish, setDisplayEnglish, colorScheme, setColorScheme, toonkorUrl, setToonkorUrl, autoFetchToonkorUrl, setAutoFetchToonkorUrl } = useContext(SettingsContext);
  const [loading, setLoading] = useState(false);
  const [inputUrl, setInputUrl] = useInputState<string>(toonkorUrl);

    const sumbmitToonkorUrl = async() => {
        const apiUrl = "/api/set_toonkor_url";
        setLoading(true);
        try {
          const response = await fetch(apiUrl, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({url: inputUrl})
            });
          if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
          }
          const json = await response.json();
          console.log(json.url);
          if (!json.error) {
            console.log(inputUrl);
            setToonkorUrl(inputUrl);
          }
          else {
            throw new Error(`${json.error}`)
          };
        } catch (error: any) {
          console.error(error.message);
        }
        setLoading(false);
      }

  return (
    <Drawer
      opened={settingsOpened}
      onClose={closeSettings}
      position="right"
      closeButtonProps={{
        iconSize: '35',
        radius: '30',
      }}
    >
      <Title>Settings</Title>
      <Group>
          <TextInput label="Toonkor URL" value={inputUrl} onChange={setInputUrl} disabled={loading}/>
          {loading && <Button loading loaderProps={{ type: 'dots' }}>Loading</Button>}
          {!loading && <Button onClick={sumbmitToonkorUrl}>Save</Button>}
      </Group>
      <Switch
        label="Auto-fetch Toonkor Url"
        labelPosition="left"
        checked={autoFetchToonkorUrl === true}
        onChange={(event) => setAutoFetchToonkorUrl(event.currentTarget.checked)}
      />
      <Switch
        label="Display Manhwa Details in English"
        labelPosition="left"
        checked={displayEnglish}
        onChange={(event) => setDisplayEnglish(event.currentTarget.checked)}
      />
      <Switch
        label="Dark Mode"
        labelPosition="left"
        checked={colorScheme === 'dark'}
        onChange={(event) => setColorScheme(event.currentTarget.checked ? 'dark' : 'light')}
      />
    </Drawer>
  );
};

export default SettingsDrawer;
