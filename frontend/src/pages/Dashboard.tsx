import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Play, Pause, Settings, Download, Zap, Upload, Server, Activity, FileVideo, AlertCircle, CheckCircle, Clock } from 'lucide-react';

const STIVDashboard = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [velocityThreshold, setVelocityThreshold] = useState([0.5]);
  const [measurementPoints, setMeasurementPoints] = useState(12);
  const [activeTab, setActiveTab] = useState('analysis');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  
  const velocityData = [
     { time: 0, velocity: 1.2, x: 245, y: 180 },
     { time: 1, velocity: 1.8, x: 320, y: 165 },
     { time: 2, velocity: 2.1, x: 410, y: 155 },
     { time: 3, velocity: 1.9, x: 490, y: 170 },
     { time: 4, velocity: 2.3, x: 580, y: 145 },
  ];

  const processes = [
     { id: 1, name: 'Video Preprocessing', status: 'completed', progress: 100, startTime: '14:32:15', duration: '2.3s' },
     { id: 2, name: 'STIV Analysis Engine', status: 'running', progress: 67, startTime: '14:32:18', duration: '5.1s' },
     { id: 3, name: 'Velocity Calculation', status: 'queued', progress: 0, startTime: '--:--:--', duration: '--' },
     { id: 4, name: 'Data Export', status: 'queued', progress: 0, startTime: '--:--:--', duration: '--' },
  ];

  const maxVelocity = Math.max(...velocityData.map(d => d.velocity));
  const avgVelocity = velocityData.reduce((sum, d) => sum + d.velocity, 0) / velocityData.length;

  useEffect(() => {
    let interval: number;
    if (isPlaying) {
      interval = window.setInterval(() => {
        setCurrentFrame(prev => (prev + 1) % 100);
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  const handleFileUpload = useCallback((file: File | null) => {
    if (!file) return;
    setSelectedFile(file);
    setVideoUrl(URL.createObjectURL(file)); // Create a URL for the video
    setIsUploading(true);
    setUploadProgress(0);
    
    const interval = window.setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsUploading(false);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-4 h-4 text-cyan-400" />;
      case 'running': return <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />;
      case 'queued': return <Clock className="w-4 h-4 text-gray-500" />;
      default: return <AlertCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-cyan-500/20 text-cyan-300';
      case 'running': return 'bg-cyan-500/30 text-cyan-300';
      case 'queued': return 'bg-gray-700 text-gray-400';
      default: return 'bg-red-500/20 text-red-400';
    }
  };

  return (
    <div className="min-h-screen p-4 font-sans text-gray-200 bg-gray-900 sm:p-6 lg:p-8">
      <div className="mx-auto space-y-6 max-w-7xl">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-3xl font-bold text-white">STIV Analysis Dashboard</h1>
            <p className="text-gray-400">Space-Time Image Velocimetry • Real-time Flow Analysis</p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="px-3 py-1.5">
              <Zap className="w-4 h-4 mr-2" />
              Live Analysis
            </Badge>
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="analysis" className="flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Analysis
            </TabsTrigger>
            <TabsTrigger value="backend" className="flex items-center gap-2">
              <Server className="w-4 h-4" />
              Backend Processes
            </TabsTrigger>
            <TabsTrigger value="upload" className="flex items-center gap-2">
              <Upload className="w-4 h-4" />
              Upload & Process
            </TabsTrigger>
          </TabsList>

          <TabsContent value="analysis" className="space-y-6">
            <div className="grid grid-cols-12 gap-6">
              <div className="col-span-12 lg:col-span-8">
                <Card>
                  <CardHeader>
                    <CardTitle>Flow Visualization</CardTitle>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="relative overflow-hidden bg-black aspect-video rounded-b-xl">
                      {videoUrl ? (
                        <video src={videoUrl} controls className="object-cover w-full h-full" />
                      ) : (
                        <img 
                          src="https://images.unsplash.com/photo-1500939733188-a8833a590384?q=80&w=2070&auto=format&fit=crop" 
                          alt="Water flow analysis"
                          className="object-cover w-full h-full"
                        />
                      )}
                      <div className="absolute inset-0">
                        {velocityData.map((point, index) => (
                          <div
                            key={index}
                            className="absolute w-3 h-3 rounded-full velocity-indicator animate-pulse"
                            style={{
                              left: `${point.x}px`,
                              top: `${point.y}px`,
                              opacity: 0.8 + (point.velocity / maxVelocity) * 0.2
                            }}
                          >
                            <div className="absolute -top-6 -left-4 text-xs text-cyan-300 font-mono bg-black/60 px-1.5 py-0.5 rounded">
                              {point.velocity.toFixed(1)}m/s
                            </div>
                          </div>
                        ))}
                        <div className="absolute top-4 left-4 text-cyan-300">
                          <div className="flex items-center gap-2 px-2 py-1 font-mono text-sm rounded bg-black/70">
                            → Flow Direction
                          </div>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 border-t border-gray-700">
                      <div className="flex items-center gap-4">
                        <Button size="sm" onClick={() => setIsPlaying(!isPlaying)}>
                          {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        </Button>
                        <div className="flex-1">
                          <Progress value={currentFrame} className="h-2" />
                        </div>
                        <div className="font-mono text-sm text-gray-400">
                          {currentFrame}s / 100s
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              <div className="col-span-12 space-y-6 lg:col-span-4">
                <Card>
                  <CardHeader><CardTitle>Flow Metrics</CardTitle></CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-3xl font-bold metric-value">{avgVelocity.toFixed(2)}</div>
                        <div className="text-xs text-gray-400">Avg Velocity (m/s)</div>
                      </div>
                      <div className="text-center">
                        <div className="text-3xl font-bold metric-value">{maxVelocity.toFixed(2)}</div>
                        <div className="text-xs text-gray-400">Max Velocity (m/s)</div>
                      </div>
                    </div>
                    <div className="pt-2 space-y-2">
                      <div className="flex justify-between text-sm"><span>Flow Rate</span><span className="font-mono text-cyan-300">2.4 m³/s</span></div>
                      <div className="flex justify-between text-sm"><span>Measurement Points</span><span className="font-mono text-cyan-300">{measurementPoints}</span></div>
                      <div className="flex justify-between text-sm"><span>Processing FPS</span><span className="font-mono text-cyan-300">30</span></div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle>Analysis Parameters</CardTitle></CardHeader>
                  <CardContent className="space-y-5">
                    <div>
                      <Label className="block mb-2 text-sm font-medium">Velocity Threshold: {velocityThreshold[0].toFixed(1)} m/s</Label>
                      <Slider value={velocityThreshold} onValueChange={setVelocityThreshold} max={3} min={0.1} step={0.1} />
                    </div>
                    <div>
                      <Label className="block mb-2 text-sm font-medium">Measurement Points: {measurementPoints}</Label>
                      <Slider value={[measurementPoints]} onValueChange={([value]) => setMeasurementPoints(value)} max={50} min={5} step={1} />
                    </div>
                    <div className="pt-2 space-y-2">
                      <Button className="w-full">Start Analysis</Button>
                      <Button variant="outline" className="w-full"><Download className="w-4 h-4 mr-2" />Export Data</Button>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle>Velocity Timeline</CardTitle></CardHeader>
                  <CardContent>
                    <div className="relative h-40 p-4">
                      <div className="absolute inset-4">
                        <div className="flex items-end justify-between h-full gap-2">
                          {velocityData.map((point, index) => (
                            <div key={index} className="w-full rounded-t-sm velocity-indicator-bg" style={{height: `${(point.velocity / maxVelocity) * 100}%`, minHeight: '4px'}}/>
                          ))}
                        </div>
                      </div>
                      <div className="absolute flex justify-between text-xs text-gray-500 bottom-1 left-4 right-4">
                        <span>0s</span><span>2s</span><span>4s</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>
          
          <TabsContent value="backend" className="space-y-6">
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Server className="w-5 h-5" />
                    Backend Process Monitor
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {processes.map((process) => (
                      <div key={process.id} className="p-4 bg-gray-800 rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-3">
                            {getStatusIcon(process.status)}
                            <span className="font-medium">{process.name}</span>
                            <Badge className={`text-xs capitalize ${getStatusColor(process.status)}`}>
                              {process.status}
                            </Badge>
                          </div>
                          <div className="font-mono text-sm text-gray-400">
                            {process.startTime} • {process.duration}
                          </div>
                        </div>
                        <div className="space-y-2">
                          <Progress value={process.progress} className="h-2" />
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>{process.progress}% complete</span>
                            {process.status === 'running' && (
                              <span className="text-cyan-400">Processing...</span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>System Status</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                      <div className="text-3xl font-bold metric-value">98%</div>
                      <div className="text-xs text-gray-400">CPU Usage</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold metric-value">2.1GB</div>
                      <div className="text-xs text-gray-400">Memory</div>
                    </div>
                  </div>
                  <div className="pt-2 space-y-2">
                    <div className="flex justify-between text-sm"><span>Active Processes</span><span className="font-mono text-cyan-300">4</span></div>
                    <div className="flex justify-between text-sm"><span>Queue Length</span><span className="font-mono text-cyan-300">2</span></div>
                    <div className="flex justify-between text-sm"><span>Uptime</span><span className="font-mono text-cyan-300">24h 15m</span></div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Recent Logs</CardTitle></CardHeader>
                <CardContent>
                  <div className="p-3 space-y-2 overflow-y-auto bg-gray-900 rounded-md max-h-48">
                    <div className="space-y-1 font-mono text-xs">
                      <div className="text-cyan-400">14:32:20 [INFO] STIV analysis started</div>
                      <div className="text-gray-500">14:32:19 [DEBUG] Loading video frame 1247</div>
                      <div className="text-cyan-400">14:32:18 [INFO] Preprocessing complete</div>
                      <div className="text-gray-500">14:32:17 [DEBUG] Velocity threshold set to 0.5</div>
                      <div className="text-cyan-400">14:32:15 [INFO] Video upload successful</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
          
          <TabsContent value="upload" className="space-y-6">
             <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileVideo className="w-5 h-5" />
                    Video Upload
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Alert>
                     <AlertCircle className="w-4 h-4" />
                     <AlertDescription>
                       Full upload functionality requires a backend connection.
                     </AlertDescription>
                  </Alert>
                  
                  <div className="space-y-4">
                    <div>
                      <Label htmlFor="video-upload">Select Video File</Label>
                      <Input
                        id="video-upload"
                        type="file"
                        accept="video/*"
                        onChange={(e) => handleFileUpload(e.target.files?.[0] || null)}
                        disabled={isUploading}
                        className="mt-2"
                      />
                    </div>

                    {selectedFile && (
                      <div className="p-4 bg-gray-800 rounded-lg">
                        <div className="flex items-center gap-3 mb-3">
                          <FileVideo className="w-8 h-8 text-cyan-400" />
                          <div>
                            <div className="font-medium">{selectedFile.name}</div>
                            <div className="text-sm text-gray-400">
                              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                            </div>
                          </div>
                        </div>
                        
                        {isUploading && (
                          <div className="space-y-2">
                            <Progress value={uploadProgress} className="h-2" />
                            <div className="text-sm text-gray-400">
                              Uploading... {uploadProgress}%
                            </div>
                          </div>
                        )}
                        
                        {uploadProgress === 100 && !isUploading && (
                          <div className="flex items-center gap-2 text-cyan-400">
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm">Upload complete!</span>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="pt-4">
                      <Button 
                        className="w-full"
                        disabled={!selectedFile || isUploading}
                      >
                        {isUploading ? 'Processing...' : 'Start STIV Analysis'}
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Processing Queue</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
                          <span className="text-sm font-medium">river_flow_001.mp4</span>
                        </div>
                        <Badge className="bg-cyan-500/30 text-cyan-300">Processing</Badge>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Clock className="w-4 h-4 text-gray-500" />
                          <span className="text-sm font-medium">stream_analysis_002.mp4</span>
                        </div>
                        <Badge className="text-gray-400 bg-gray-700">Queued</Badge>
                      </div>
                    </div>
                    
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <CheckCircle className="w-4 h-4 text-cyan-400" />
                          <span className="text-sm font-medium">water_velocity_003.mp4</span>
                        </div>
                        <Badge className="bg-cyan-500/20 text-cyan-300">Completed</Badge>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default STIVDashboard;
