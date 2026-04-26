"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Clock, MapPin, Wifi, Camera, QrCode, Fingerprint } from "lucide-react"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface CheckInOutProps {
  currentUser: any
  setCurrentUser: (user: any) => void
}

export function CheckInOut({ currentUser, setCurrentUser }: CheckInOutProps) {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [location, setLocation] = useState("Office - Main Building")
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  const handleCheckInOut = async () => {
    setIsLoading(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))

    const now = new Date()
    setCurrentUser({
      ...currentUser,
      isCheckedIn: !currentUser.isCheckedIn,
      lastCheckIn: !currentUser.isCheckedIn ? now : currentUser.lastCheckIn,
      lastCheckOut: currentUser.isCheckedIn ? now : currentUser.lastCheckOut,
    })

    setIsLoading(false)
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Check In/Out</h2>
        <p className="text-muted-foreground">Track your attendance with one-tap check-in and check-out</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Main Check-in/out Card */}
        <Card className="col-span-2 md:col-span-1">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4">
              <Avatar className="h-20 w-20">
                <AvatarImage src="/placeholder.svg?height=80&width=80" />
                <AvatarFallback className="text-2xl">
                  {currentUser.name
                    .split(" ")
                    .map((n: string) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
            </div>
            <CardTitle className="text-2xl">{currentUser.name}</CardTitle>
            <CardDescription>{currentUser.department} Department</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Current Time */}
            <div className="text-center space-y-2">
              <div className="text-4xl font-mono font-bold">{formatTime(currentTime)}</div>
              <div className="text-sm text-muted-foreground">{formatDate(currentTime)}</div>
            </div>

            {/* Status */}
            <div className="flex justify-center">
              <Badge variant={currentUser.isCheckedIn ? "default" : "secondary"} className="text-lg px-4 py-2">
                {currentUser.isCheckedIn ? "Checked In" : "Checked Out"}
              </Badge>
            </div>

            {/* Location */}
            <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <MapPin className="h-4 w-4" />
              <span>{location}</span>
            </div>

            {/* Check-in/out Button */}
            <Button
              onClick={handleCheckInOut}
              disabled={isLoading}
              size="lg"
              className="w-full text-lg py-6"
              variant={currentUser.isCheckedIn ? "destructive" : "default"}
            >
              {isLoading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                  Processing...
                </div>
              ) : (
                <>
                  <Clock className="h-5 w-5 mr-2" />
                  {currentUser.isCheckedIn ? "Check Out" : "Check In"}
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Alternative Check-in Methods */}
        <Card>
          <CardHeader>
            <CardTitle>Alternative Check-in Methods</CardTitle>
            <CardDescription>Multiple ways to track your attendance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button variant="outline" className="w-full justify-start" disabled>
              <QrCode className="h-4 w-4 mr-2" />
              QR Code Scan
              <Badge variant="secondary" className="ml-auto">
                Coming Soon
              </Badge>
            </Button>
            <Button variant="outline" className="w-full justify-start" disabled>
              <Fingerprint className="h-4 w-4 mr-2" />
              Biometric Scan
              <Badge variant="secondary" className="ml-auto">
                Coming Soon
              </Badge>
            </Button>
            <Button variant="outline" className="w-full justify-start" disabled>
              <Camera className="h-4 w-4 mr-2" />
              Facial Recognition
              <Badge variant="secondary" className="ml-auto">
                Coming Soon
              </Badge>
            </Button>
            <Button variant="outline" className="w-full justify-start" disabled>
              <Wifi className="h-4 w-4 mr-2" />
              Wi-Fi Detection
              <Badge variant="secondary" className="ml-auto">
                Coming Soon
              </Badge>
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Today's Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Today's Activity</CardTitle>
          <CardDescription>Your attendance record for today</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {currentUser.lastCheckIn && (
              <div className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-950 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 bg-green-500 rounded-full" />
                  <span className="font-medium">Checked In</span>
                </div>
                <span className="text-sm text-muted-foreground">{formatTime(currentUser.lastCheckIn)}</span>
              </div>
            )}

            {currentUser.lastCheckOut && (
              <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-950 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="h-2 w-2 bg-red-500 rounded-full" />
                  <span className="font-medium">Checked Out</span>
                </div>
                <span className="text-sm text-muted-foreground">{formatTime(currentUser.lastCheckOut)}</span>
              </div>
            )}

            {!currentUser.lastCheckIn && !currentUser.lastCheckOut && (
              <Alert>
                <Clock className="h-4 w-4" />
                <AlertDescription>
                  No activity recorded for today. Click the check-in button to start tracking your time.
                </AlertDescription>
              </Alert>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
