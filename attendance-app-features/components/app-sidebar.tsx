"use client"

import { Clock, Home, Settings, Users, BarChart3 } from "lucide-react"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"

const menuItems = [
  {
    title: "Dashboard",
    url: "dashboard",
    icon: Home,
  },
  {
    title: "Check In/Out",
    url: "checkin",
    icon: Clock,
  },
  {
    title: "Employees",
    url: "employees",
    icon: Users,
  },
  {
    title: "Reports",
    url: "reports",
    icon: BarChart3,
  },
  {
    title: "Settings",
    url: "settings",
    icon: Settings,
  },
]

interface AppSidebarProps {
  activeView: string
  setActiveView: (view: string) => void
  currentUser: any
}

export function AppSidebar({ activeView, setActiveView, currentUser }: AppSidebarProps) {
  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center gap-3 p-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <Clock className="h-4 w-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold">AttendanceTracker</span>
            <span className="text-xs text-muted-foreground">Pro Version</span>
          </div>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton onClick={() => setActiveView(item.url)} isActive={activeView === item.url}>
                    <item.icon />
                    <span>{item.title}</span>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-center gap-3 p-2">
          <Avatar className="h-8 w-8">
            <AvatarImage src="/placeholder.svg?height=32&width=32" />
            <AvatarFallback>
              {currentUser.name
                .split(" ")
                .map((n: string) => n[0])
                .join("")}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col flex-1">
            <span className="text-sm font-medium">{currentUser.name}</span>
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">{currentUser.department}</span>
              <Badge variant={currentUser.isCheckedIn ? "default" : "secondary"} className="text-xs">
                {currentUser.isCheckedIn ? "Checked In" : "Checked Out"}
              </Badge>
            </div>
          </div>
        </div>
      </SidebarFooter>
    </Sidebar>
  )
}
