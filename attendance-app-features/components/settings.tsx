"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { SettingsIcon, Bell, Shield, Clock, MapPin, Smartphone, Save } from "lucide-react"

export function Settings() {
  const [notifications, setNotifications] = useState({
    checkInReminders: true,
    lateArrivalAlerts: true,
    leaveApprovals: false,
    weeklyReports: true,
  })

  const [workingHours, setWorkingHours] = useState({
    startTime: "09:00",
    endTime: "17:00",
    timezone: "UTC-5",
  })

  const [geofencing, setGeofencing] = useState({
    enabled: false,
    radius: "100",
    strictMode: false,
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">Configure your attendance tracking preferences and system settings</p>
      </div>

      {/* General Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <SettingsIcon className="h-5 w-5" />
            General Settings
          </CardTitle>
          <CardDescription>Basic configuration for your attendance system</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="company-name">Company Name</Label>
              <Input id="company-name" defaultValue="TechCorp Inc." />
            </div>
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <Select defaultValue="UTC-5">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="UTC-8">Pacific Time (UTC-8)</SelectItem>
                  <SelectItem value="UTC-7">Mountain Time (UTC-7)</SelectItem>
                  <SelectItem value="UTC-6">Central Time (UTC-6)</SelectItem>
                  <SelectItem value="UTC-5">Eastern Time (UTC-5)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="office-address">Office Address</Label>
            <Input id="office-address" defaultValue="123 Business St, Tech City, TC 12345" />
          </div>
        </CardContent>
      </Card>

      {/* Working Hours */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Working Hours
          </CardTitle>
          <CardDescription>Set standard working hours and break times</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="start-time">Start Time</Label>
              <Input
                id="start-time"
                type="time"
                value={workingHours.startTime}
                onChange={(e) => setWorkingHours({ ...workingHours, startTime: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end-time">End Time</Label>
              <Input
                id="end-time"
                type="time"
                value={workingHours.endTime}
                onChange={(e) => setWorkingHours({ ...workingHours, endTime: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="break-duration">Break Duration (minutes)</Label>
            <Input id="break-duration" type="number" defaultValue="60" />
          </div>

          <div className="space-y-2">
            <Label htmlFor="grace-period">Grace Period for Late Arrival (minutes)</Label>
            <Input id="grace-period" type="number" defaultValue="15" />
          </div>
        </CardContent>
      </Card>

      {/* Geofencing & Location */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Geofencing & Location
          </CardTitle>
          <CardDescription>Configure location-based attendance tracking</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Enable Geofencing</Label>
              <p className="text-sm text-muted-foreground">
                Require employees to be within a specific location to check in
              </p>
            </div>
            <Switch
              checked={geofencing.enabled}
              onCheckedChange={(checked) => setGeofencing({ ...geofencing, enabled: checked })}
            />
          </div>

          {geofencing.enabled && (
            <>
              <div className="space-y-2">
                <Label htmlFor="geofence-radius">Geofence Radius (meters)</Label>
                <Input
                  id="geofence-radius"
                  type="number"
                  value={geofencing.radius}
                  onChange={(e) => setGeofencing({ ...geofencing, radius: e.target.value })}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Strict Mode</Label>
                  <p className="text-sm text-muted-foreground">Prevent check-in/out outside the geofenced area</p>
                </div>
                <Switch
                  checked={geofencing.strictMode}
                  onCheckedChange={(checked) => setGeofencing({ ...geofencing, strictMode: checked })}
                />
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notifications
          </CardTitle>
          <CardDescription>Manage notification preferences for attendance events</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Check-in Reminders</Label>
              <p className="text-sm text-muted-foreground">Send reminders to employees who haven't checked in</p>
            </div>
            <Switch
              checked={notifications.checkInReminders}
              onCheckedChange={(checked) => setNotifications({ ...notifications, checkInReminders: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Late Arrival Alerts</Label>
              <p className="text-sm text-muted-foreground">Notify managers when employees arrive late</p>
            </div>
            <Switch
              checked={notifications.lateArrivalAlerts}
              onCheckedChange={(checked) => setNotifications({ ...notifications, lateArrivalAlerts: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Leave Approval Notifications</Label>
              <p className="text-sm text-muted-foreground">Send notifications for leave requests and approvals</p>
            </div>
            <Switch
              checked={notifications.leaveApprovals}
              onCheckedChange={(checked) => setNotifications({ ...notifications, leaveApprovals: checked })}
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Weekly Reports</Label>
              <p className="text-sm text-muted-foreground">Receive weekly attendance summary reports</p>
            </div>
            <Switch
              checked={notifications.weeklyReports}
              onCheckedChange={(checked) => setNotifications({ ...notifications, weeklyReports: checked })}
            />
          </div>
        </CardContent>
      </Card>

      {/* Security & Privacy */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Security & Privacy
          </CardTitle>
          <CardDescription>Configure security settings and data privacy options</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Two-Factor Authentication</Label>
              <p className="text-sm text-muted-foreground">Require 2FA for admin access</p>
            </div>
            <Badge variant="secondary">Coming Soon</Badge>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Biometric Authentication</Label>
              <p className="text-sm text-muted-foreground">Enable fingerprint or face recognition for check-in</p>
            </div>
            <Badge variant="secondary">Coming Soon</Badge>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Data Encryption</Label>
              <p className="text-sm text-muted-foreground">All attendance data is encrypted at rest and in transit</p>
            </div>
            <Badge variant="default">Enabled</Badge>
          </div>

          <div className="space-y-2">
            <Label htmlFor="data-retention">Data Retention Period (months)</Label>
            <Input id="data-retention" type="number" defaultValue="24" />
          </div>
        </CardContent>
      </Card>

      {/* Mobile App Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Smartphone className="h-5 w-5" />
            Mobile App Settings
          </CardTitle>
          <CardDescription>Configure mobile application preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Offline Mode</Label>
              <p className="text-sm text-muted-foreground">Allow check-in/out when offline (syncs when online)</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Background Location</Label>
              <p className="text-sm text-muted-foreground">Track location in background for automatic check-in</p>
            </div>
            <Badge variant="secondary">Coming Soon</Badge>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Push Notifications</Label>
              <p className="text-sm text-muted-foreground">Receive notifications on mobile device</p>
            </div>
            <Switch defaultChecked />
          </div>

          <div className="space-y-2">
            <Label htmlFor="check-in-radius">Auto Check-in Radius (meters)</Label>
            <Input id="check-in-radius" type="number" defaultValue="50" />
          </div>
        </CardContent>
      </Card>

      {/* Save Settings */}
      <div className="flex justify-end">
        <Button size="lg">
          <Save className="h-4 w-4 mr-2" />
          Save All Settings
        </Button>
      </div>
    </div>
  )
}
