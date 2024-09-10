import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Library from './pages/Library';
import Browse from './pages/Browse';
import Manhwa from './pages/Manhwa';
import Chapter from './pages/Chapter';


const router = createBrowserRouter([
  {
    path: '/',
    element: <Library />,
  },
  {
    path: '/manhwa/:toonkorId',
    element: <Manhwa />,
  },
  {
    path: '/manhwa/:toonkorId/:chapter/:choice',
    element: <Chapter />,
  },  
  {
    path: '/library',
    element: <Library />,
  },
  {
    path: '/browse',
    element: <Browse />,
  },
]);

export function Router() {
  return <RouterProvider router={router} />;
}
