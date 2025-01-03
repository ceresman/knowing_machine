import { useState } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent } from './ui/card';
import { ZoomIn, ZoomOut } from 'lucide-react';
import { Button } from './ui/button';

const ZOOM_LEVELS = [5, 6, 7, 8, 9, 10];

export function ImageViewer() {
  const [currentZoom, setCurrentZoom] = useState(5);
  
  return (
    <div className="flex flex-col gap-4 p-4 w-full max-w-screen-xl mx-auto">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => setCurrentZoom(Math.max(5, currentZoom - 1))}
            disabled={currentZoom <= 5}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
          <Select
            value={currentZoom.toString()}
            onValueChange={(value) => setCurrentZoom(parseInt(value))}
          >
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Zoom Level" />
            </SelectTrigger>
            <SelectContent>
              {ZOOM_LEVELS.map((level) => (
                <SelectItem key={level} value={level.toString()}>
                  Zoom Level {level}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button 
            variant="outline" 
            size="icon"
            onClick={() => setCurrentZoom(Math.min(10, currentZoom + 1))}
            disabled={currentZoom >= 10}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
        </div>
      </div>
      
      <Card className="w-full overflow-hidden">
        <CardContent className="p-0">
          <div className="relative w-full h-screen max-h-[80vh] overflow-auto">
            <img
              src={`/merged_tiles/merged_zoom_${currentZoom}.png`}
              alt={`Visualization at zoom level ${currentZoom}`}
              className="w-full h-auto"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
