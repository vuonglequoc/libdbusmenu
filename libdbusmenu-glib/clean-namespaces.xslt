<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:dox="http://www.ayatana.org/dbus/dox.dtd">
	<xsl:template match="*|@*">
		<xsl:copy>
			<xsl:apply-templates select="*|@*" />
		</xsl:copy>
	</xsl:template>
	<xsl:template match="@dox:*|dox:*"/>
</xsl:stylesheet>

