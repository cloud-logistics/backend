package com.hnair.iot.util;

import com.google.common.hash.Hashing;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.net.NetworkInterface;
import java.net.SocketException;
import java.nio.charset.StandardCharsets;
import java.util.Enumeration;

public class DeviceUtil {

	private static String deviceId;

	public static String getDeviceSN() {
		if (deviceId == null) {
			try {
				deviceId = Hashing.md5().hashString(getMac(), StandardCharsets.UTF_8).toString();
			} catch (SocketException e) {
				deviceId = getDeviceName();
			}
		}
		return deviceId;
	}

	public static String getDeviceName(String name) {
		return name;
	}

	public static String getDeviceName() {
		return System.getProperty("user.name");
	}

	public static String getDeviceInfo() {
		return new StringBuilder(System.getProperty("os.name")).append(" ").append("(")
				.append(System.getProperty("os.version")).append(", ").append(System.getProperty("os.arch")).append(")")
				.toString();
	}

	/**
	 * 获取主板序列号
	 * 
	 * @return
	 */
	public static String getMotherboardSN() {
		String result = "";
		try {
			File file = File.createTempFile("realhowto", ".vbs");
			file.deleteOnExit();
			FileWriter fw = new FileWriter(file);

			String vbs = "Set objWMIService = GetObject(\"winmgmts:\\\\.\\root\\cimv2\")\n"
					+ "Set colItems = objWMIService.ExecQuery _ \n" + "   (\"Select * from Win32_BaseBoard\") \n"
					+ "For Each objItem in colItems \n" + "    Wscript.Echo objItem.SerialNumber \n"
					+ "    exit for  ' do the first cpu only! \n" + "Next \n";

			fw.write(vbs);
			fw.close();
			Process p = Runtime.getRuntime().exec("cscript //NoLogo " + file.getPath());
			BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line;
			while ((line = input.readLine()) != null) {
				result += line;
			}
			input.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return result.trim();
	}

	/**
	 * 获取硬盘序列号
	 *
	 * @param drive
	 *            盘符
	 * @return
	 */
	public static String getHardDiskSN(String drive) {
		String result = "";
		try {
			File file = File.createTempFile("realhowto", ".vbs");
			file.deleteOnExit();
			FileWriter fw = new FileWriter(file);

			String vbs = "Set objFSO = CreateObject(\"Scripting.FileSystemObject\")\n"
					+ "Set colDrives = objFSO.Drives\n" + "Set objDrive = colDrives.item(\"" + drive + "\")\n"
					+ "Wscript.Echo objDrive.SerialNumber"; // see note
			fw.write(vbs);
			fw.close();
			Process p = Runtime.getRuntime().exec("cscript //NoLogo " + file.getPath());
			BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line;
			while ((line = input.readLine()) != null) {
				result += line;
			}
			input.close();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return result.trim();
	}

	/**
	 * 获取CPU序列号
	 *
	 * @return
	 */
	public static String getCPUSerial() {
		String result = "";
		try {
			File file = File.createTempFile("tmp", ".vbs");
			file.deleteOnExit();
			FileWriter fw = new FileWriter(file);
			String vbs = "Set objWMIService = GetObject(\"winmgmts:\\\\.\\root\\cimv2\")\n"
					+ "Set colItems = objWMIService.ExecQuery _ \n" + "   (\"Select * from Win32_Processor\") \n"
					+ "For Each objItem in colItems \n" + "    Wscript.Echo objItem.ProcessorId \n"
					+ "    exit for  ' do the first cpu only! \n" + "Next \n";

			// + " exit for \r\n" + "Next";
			fw.write(vbs);
			fw.close();
			Process p = Runtime.getRuntime().exec("cscript //NoLogo " + file.getPath());
			BufferedReader input = new BufferedReader(new InputStreamReader(p.getInputStream()));
			String line;
			while ((line = input.readLine()) != null) {
				result += line;
			}
			input.close();
			file.delete();
		} catch (Exception e) {
			e.fillInStackTrace();
		}
		if (result.trim().length() < 1 || result == null) {
			result = "无CPU_ID被读取";
		}
		return result.trim();
	}

	/**
	 * 获取MAC地址
	 * 
	 * @throws SocketException
	 */
	public static String getMac() throws SocketException {
		String result = "";
		Enumeration<NetworkInterface> e = NetworkInterface.getNetworkInterfaces();// 返回所有网络接口的一个枚举实例
		while (e.hasMoreElements()) {
			NetworkInterface network = e.nextElement();// 获得当前网络接口
			if (network != null) {
				if (network.getHardwareAddress() != null) {
					// 获得MAC地址
					// 结果是一个byte数组，每项是一个byte，我们需要通过parseByte方法转换成常见的十六进制表示
					byte[] addres = network.getHardwareAddress();
					StringBuffer sb = new StringBuffer();
					if (addres != null && addres.length > 1) {
						sb.append(parseByte(addres[0])).append(":").append(parseByte(addres[1])).append(":")
								.append(parseByte(addres[2])).append(":").append(parseByte(addres[3])).append(":")
								.append(parseByte(addres[4])).append(":").append(parseByte(addres[5]));
						if (!network.isLoopback() && network.isUp() && !network.isPointToPoint()
								&& !network.isVirtual())
							result += sb;
					}
				}
			} else {
				return result;
			}
		}
		return result;
	}

	private static String parseByte(byte b) {
		int intValue = 0;
		if (b >= 0) {
			intValue = b;
		} else {
			intValue = 256 + b;
		}
		return Integer.toHexString(intValue);
	}

	public static void main(String[] args) throws SocketException {
//		System.out.println("CPU SN:" + DeviceUtil.getCPUSerial());
//		System.out.println("主板 SN:" + DeviceUtil.getMotherboardSN());
//		System.out.println("C盘 SN:" + DeviceUtil.getHardDiskSN("c"));
		System.out.println("MAC  SN:" + DeviceUtil.getDeviceSN());
	}

}
