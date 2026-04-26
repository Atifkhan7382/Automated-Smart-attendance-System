"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, LineChart, Line } from "recharts"
import { Download, Calendar, TrendingUp, Clock, Users } from "lucide-react"

const weeklyData = [
  { week: "Week 1", attendance: 94, late: 6, absent: 8 },
  { week: "Week 2", attendance: 96, late: 4, absent: 6 },
  { week: "Week 3", attendance: 92, late: 8, absent: 10 },
  { week: "Week 4", attendance: 98, late: 2, absent: 4 },
]

const monthlyTrends = [
  { month: "Jan", rate: 94 },
  { month: "Feb", rate: 96 },
  { month: "Mar", rate: 92 },
  { month: "Apr", rate: 98 },
  { month: "May", rate: 95 },
  { month: "Jun", rate: 97 },
]

const detailedReports = [
  {
    id: "1",
    employee: "John Doe",
    department: "IT",
    daysPresent: 22,
    daysAbsent: 1,
    lateArrivals: 2,
    totalHours: "176h 30m",
    attendanceRate: "96%",
  },
  {
    id: "2",
    employee: "Alice Johnson",
    department: "HR",
    daysPresent: 23,
    daysAbsent: 0,
    lateArrivals: 1,
    totalHours: "184h 00m",
    attendanceRate: "100%",
  },
  {
    id: "3",
    employee: "Bob Smith",
    department: "Sales",
    daysPresent: 20,
    daysAbsent: 3,
    lateArrivals: 4,
    totalHours: "160h 15m",
    attendanceRate: "87%",
  },
  {
    id: "4",
    employee: "Carol Davis",
    department: "Marketing",
    daysPresent: 18,
    daysAbsent: 5,
    lateArrivals: 1,
    totalHours: "144h 45m",
    attendanceRate: "78%",
  },
]

export function AttendanceReports() {
  const [selectedPeriod, setSelectedPeriod] = useState("monthly")
  const [selectedDepartment, setSelectedDepartment] = useState("all")

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Attendance Reports</h2>
        <p className="text-muted-foreground">Comprehensive attendance analytics and reporting</p>
      </div>

      {/* Report Controls */}
      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div>
              <CardTitle>Report Filters</CardTitle>
              <CardDescription>Customize your attendance reports</CardDescription>
            </div>
            <Button>
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Select period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
                <SelectItem value="quarterly">Quarterly</SelectItem>
                <SelectItem value="yearly">Yearly</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedDepartment} onValueChange={setSelectedDepartment}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Select department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                <SelectItem value="IT">IT</SelectItem>
                <SelectItem value="HR">HR</SelectItem>
                <SelectItem value="Sales">Sales</SelectItem>
                <SelectItem value="Marketing">Marketing</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Attendance</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">95.2%</div>
            <p className="text-xs text-muted-foreground">+2.1% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Work Hours</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">8,240h</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Late Arrivals</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">23</div>
            <p className="text-xs text-muted-foreground">-8 from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Perfect Attendance</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">Employees this month</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {/* Weekly Attendance Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Weekly Attendance Overview</CardTitle>
            <CardDescription>Attendance, late arrivals, and absences by week</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={{
                attendance: {
                  label: "Attendance %",
                  color: "hsl(var(--chart-1))",
                },
                late: {
                  label: "Late Arrivals",
                  color: "hsl(var(--chart-2))",
                },
                absent: {
                  label: "Absences",
                  color: "hsl(var(--chart-3))",
                },
              }}
              className="h-[300px]"
            >
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData}>
                  <XAxis dataKey="week" />
                  <YAxis />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Bar dataKey="attendance" fill="var(--color-attendance)" />
                  <Bar dataKey="late" fill="var(--color-late)" />
                  <Bar dataKey="absent" fill="var(--color-absent)" />
                </BarChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>

        {/* Monthly Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Monthly Attendance Trends</CardTitle>
            <CardDescription>Attendance rate trends over the past 6 months</CardDescription>
          </CardHeader>
          <CardContent>
            <ChartContainer
              config={{
                rate: {
                  label: "Attendance Rate %",
                  color: "hsl(var(--chart-1))",
                },
              }}
              className="h-[300px]"
            >
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={monthlyTrends}>
                  <XAxis dataKey="month" />
                  <YAxis domain={[85, 100]} />
                  <ChartTooltip content={<ChartTooltipContent />} />
                  <Line
                    type="monotone"
                    dataKey="rate"
                    stroke="var(--color-rate)"
                    strokeWidth={2}
                    dot={{ fill: "var(--color-rate)" }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Employee Reports */}
      <Card>
        <CardHeader>
          <CardTitle>Employee Attendance Details</CardTitle>
          <CardDescription>Detailed attendance breakdown by employee</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Days Present</TableHead>
                  <TableHead>Days Absent</TableHead>
                  <TableHead>Late Arrivals</TableHead>
                  <TableHead>Total Hours</TableHead>
                  <TableHead>Attendance Rate</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {detailedReports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell className="font-medium">{report.employee}</TableCell>
                    <TableCell>{report.department}</TableCell>
                    <TableCell>{report.daysPresent}</TableCell>
                    <TableCell>{report.daysAbsent}</TableCell>
                    <TableCell>{report.lateArrivals}</TableCell>
                    <TableCell>{report.totalHours}</TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          Number.parseInt(report.attendanceRate) >= 95
                            ? "default"
                            : Number.parseInt(report.attendanceRate) >= 85
                              ? "secondary"
                              : "destructive"
                        }
                      >
                        {report.attendanceRate}
                      </Badge>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
