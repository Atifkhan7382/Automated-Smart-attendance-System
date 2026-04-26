"use client"

import { useState } from "react"
import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Dashboard } from "@/components/dashboard"
import { EmployeeManagement } from "@/components/employee-management"
import { AttendanceReports } from "@/components/attendance-reports"
import { CheckInOut } from "@/components/check-in-out"
import { Settings } from "@/components/settings"

export default function AttendanceApp() {
  const [activeView, setActiveView] = useState("dashboard")
  const [currentUser, setCurrentUser] = useState({
    id: "1",
    name: "John Doe",
    role: "admin",
    department: "IT",
    isCheckedIn: false,
    lastCheckIn: null as Date | null,
    lastCheckOut: null as Date | null,
  })

  const renderActiveView = () => {
    switch (activeView) {
      case "dashboard":
        return <Dashboard currentUser={currentUser} />
      case "checkin":
        return <CheckInOut currentUser={currentUser} setCurrentUser={setCurrentUser} />
      case "employees":
        return <EmployeeManagement />
      case "reports":
        return <AttendanceReports />
      case "settings":
        return <Settings />
      default:
        return <Dashboard currentUser={currentUser} />
    }
  }

  return (
    <SidebarProvider>
      <AppSidebar activeView={activeView} setActiveView={setActiveView} currentUser={currentUser} />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <SidebarTrigger className="-ml-1" />
          <div className="flex items-center gap-2">
            <h1 className="text-lg font-semibold">AttendanceTracker Pro</h1>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4">{renderActiveView()}</div>
      </SidebarInset>
    </SidebarProvider>
  )
}
